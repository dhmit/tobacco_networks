import copy
import json
import re
import csv
from collections import Counter, defaultdict
from pathlib import Path

from IPython import embed
from nameparser import HumanName
from nameparser.config import CONSTANTS

import unittest

CONSTANTS.titles.remove(*CONSTANTS.titles)


class Person:

    def __init__(self, name_raw='', last='', first='', middle='', positions=None, aliases=None,
                 count=0):

        if name_raw:
            first, middle, last, positions = self.parse_raw_name(name_raw)

        if positions is None:
            positions = {}

        # by default, the raw name is an alias of the person
        # (we're changing the first/middle names based on new information, so keeping the original
        # name as an alias is important
        if aliases is None:
            if name_raw is None:
                aliases = []
            else:
                aliases = [name_raw]

        self.last = last.upper()
        self.first = first.upper()
        self.middle = middle.upper()
        self.positions = set()
        for i in positions:
            cleaned = re.sub('\.', '', i)
            self.positions.add(cleaned.upper())
        self.aliases = aliases
        self.count = count

    def __repr__(self):
        s = f'{self.first} {self.middle} {self.last}'
        if self.positions:
            s += "(" + ", ".join(self.positions) + ")"
        return s

    def __eq__(self, other):
        return (
            self.last == other.last and
            self.first == other.first and
            self.middle == other.middle and
            sorted(self.positions) == sorted(other.positions)
        )

    def copy(self):
        return Person(last=self.last, first=self.first, middle=self.middle,
                      positions=copy.deepcopy(self.positions),
                      aliases=copy.deepcopy(self.aliases), count=self.count)

    def __hash__(self):
        return hash(f'{self.last} {self.first} {self.middle} {self.positions}')

    def stemmed(self):
        return f'{self.last} {self.first} {self.middle}'

    @staticmethod
    def parse_raw_name(name_raw: str) -> (str, str, str, set):
        """
        Parses a (usually messy) raw name and returns
        first, middle, last names and a set of extracted positions

        :param name_raw: str
        :return: str, str, str, set


        Parses name and returns as human name
        >>> n = Person('TEAGUE CE JR')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Teague', 'C', 'E', 'JR')


        >>> n = Person('teague, ce jr')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Teague', 'C', 'E', 'JR')


        >>> n = Person('Teague, Claude Edward, Jr., Ph.D. ')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Teague', 'Claude', 'Edward', 'JR., PH.D.')

        >>> n = Person('Teague, J - BAT')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Teague', 'J', '', 'BAT')

        >>> n = Person('BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS GENERAL')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Baker', 'T', 'E', 'NATIONAL ASSOCIATION OF ATTORNEYS GENERAL')

        >>> n = Person('BAKER-cj')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Baker', 'C', 'J', '')

        JR and SR are by default recognized as titles -> turn off through CONSTANTS.
        >>> n = Person('Baker, JR')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Baker', 'J', 'R', '')

        >>> n = Person('DUNN WL #')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Dunn', 'W', 'L', '')

        >>> n = Person('Dunn, W. L.')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Dunn', 'W', 'L', '')

        >>> n = Person('TEMKO SL, COVINGTON AND BURLING')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Temko', 'S', 'L', 'COVINGTON AND BURLING')

        >>> n = Person('Temko, Stanley L [Privlog:] TEMKO,SL')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Temko', 'Stanley', 'L', '')

        >>> n = Person('Temko-SL, Covington & Burling')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Temko', 'S', 'L', 'COVINGTON & BURLING')

        >>> n = Person('HENSON, A. (AMERICAN SENIOR VICE PRESIDENT AND GENERAL COUNSEL)')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Henson', 'A', '', 'AMERICAN SENIOR VICE PRESIDENT AND GENERAL COUNSEL')

        >>> n = Person('HENSON, A. (CHADBOURNE, PARKE, WHITESIDE & WOLFF, AMERICAN OUTSIDE COUNSEL) (HANDWRITTEN NOTES)')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Henson', 'A', '', 'CHADBOURNE, PARKE, WHITESIDE & WOLFF, AMERICAN OUTSIDE COUNSEL HANDWRITTEN NOTES')

        >>> n = Person('Holtzman, A.,  Murray, J. ,  Henson, A. ,  Pepples, E. ,  Stevens, A. ,  Witt, S.')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Holtzman', 'A', '', '')

        >>> n = Person('Holtz, Jacob, Jacob & Medinger')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Holtz', 'Jacob', '', 'JACOB & MEDINGER')

        # This one breaks. But I don't think it can be avoided.
        >>> n = Person('Holtz, Jacob Alexander, Jacob & Medinger')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Holtz', '', '', 'JACOB ALEXANDER, JACOB & MEDINGER')

        >>> n = Person('PROCTOR DF, JOHNS HOPKINS SCHOOL OF HYGIENE')
        >>> n.last, n.first, n.middle, " ".join(n.positions).upper()
        ('Proctor', 'D', 'F', 'JOHNS HOPKINS SCHOOL OF HYGIENE')

        """

        # remove privlog info, e.g. 'Temko, Stanley L [Privlog:] TEMKO,SL'. It confuses
        # the name parser
        # TODO: figure out if Privlog contains position information
        privlog_id = name_raw.find('[Privlog:]')
        if privlog_id == 0:
            name_raw = name_raw[privlog_id:]
        elif privlog_id > 0:
            name_raw = name_raw[:name_raw.find('[Privlog:]')]
        else:
            pass

        # position is often attached with a dash,
        # e.g. 'BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS'
        if name_raw.find(" - ") > -1 and len(name_raw.split(' - ')) == 2:
            name_raw, extracted_position = name_raw.split(" - ")
            extracted_positions = {extracted_position.strip()}
        else:
            extracted_positions = set()

        # extract positions in parens e.g. Henson, A (Chadbourne & Park)
        paren_positions = re.findall(r'\([^(]+\)', name_raw)
        for position in paren_positions:
            extracted_positions.add(position.strip(',#() '))
            name_raw = name_raw.replace(position, '')

        institution_regexes = [

            # TI/CTR
            r'[,#] Tobacco Inst.+$',
            r'[\(\,\#] ?SAB Exec.*$',

            # American Tobacco
            r'[(,#] ?American .+$',
            r'[\(\,\#] ?Amer Brands.*$',
            r'[,#] American Tob',
            r'[,#] Atco.*$',

            # PM
            r'[\(\,\#] ?Philip Morris.*$',

            # RJR
            r'[\(\,\#] ?RJR.*$',

            # LAW FIRMS
            r'[\(\,\#] ?Arnold &.*$',
            r'[\(\,\#] ?Chadbourne.*$',
            r'[,#] COVINGTON [AB&]*.+$',
            r'[,#] Foster [&A]*.+$',
            r'[,#] JACOB [A&]*.+$',

            r'[\(\,\#] ?Philip Morris.*$',

            # Universities
            # match a ( or , or # at the beginning, then some characters that
            # aren't (,# until the end of the string
            r'[\(\,\#][^\(\,\#]+ Univ\b.*$',

            # Univ is fine if it appears at the end of a string (don't want to match in the
            # middle of a string, e.g "Universal"
            r'[\(\,\#][^\(\,\#]+ School\b.*$',

            # Organizations
            r'[\(\,\#][^\(\,\#]+ Federal Trade Commission.*$',

        ]
        for institution in institution_regexes:
            extracted_institution = re.search(institution, name_raw, re.IGNORECASE)
            if extracted_institution:
                extracted_positions.add(extracted_institution.group().strip(',#() '))
                name_raw = name_raw[:name_raw.find(extracted_institution.group())]

        # remove #
        name_raw = name_raw.strip("#").strip()

        # DUNN-W -> Dunn W
        # TODO this does not seem correct. maybe return last, first?
        if name_raw[-2] == '-':
            name_raw = name_raw[:-2] + " " + name_raw[-1:]

        # DUNN-WL -> DUNN WL
        if len(name_raw) > 2 and name_raw[-3] == '-':
            name_raw = name_raw[:-3] + " " + name_raw[-2:]

        name = HumanName(name_raw)

        # e.g. Dunn W -> parsed as last name W. -> switch first/last
        if len(name.last) <= 2 < len(name.first):
            name.first, name.last = name.last, name.first

        # remove periods from initials
        if len(name.first) == 2 and name.first[1] == '.':
            name.first = name.first[0]
        if len(name.middle) == 2 and name.middle[1] == '.':
            name.middle = name.middle[0]

        # If first name is length 2 (Teague, CE), the two letters are most likely initials.
        if len(name.first) == 2:
            name.middle = name.first[1].upper()
            name.first = name.first[0].upper()

        # If first and middle initials have periods but not spaces -> separate, e.g. "R.K. Teague"
        if re.match(r'[a-zA-Z]\.[a-zA-Z]\.', name.first):
            name.middle = name.first[2]
            name.first = name.first[0]

        name.last = name.last.capitalize()
        name.first = name.first.capitalize()
        name.middle = name.middle.capitalize()

        # if multiple names are passed, they often end up in the middle name
        # e.g. 'Holtzman, A.,  Murray, J. ,  Henson, A.  -> only allow one comma or set to empty
        if name.middle.count(',') > 1:
            name.middle = ''

        if len(name.suffix) > 20 and name.suffix.count('.') > 2:
            name.suffix = ''

        if name.suffix:
            extracted_positions.add(name.suffix)

        return name.first, name.middle, name.last, extracted_positions


class PeopleDatabase:

    def __init__(self):
        self.people = set()
        self.aliases = {}

    def add_person_raw(self, name_raw: str, count=0):
        new_p = Person(name_raw=name_raw, count=count)
        self.people.add(new_p)

    def create_positions_csv(self):
        """
        Makes a Counter of all positions appearing in db,
        Translates this info into a CSV,
        1st Col = raw name
        2nd Col = count in Counter
        3rd Col = authoritative name– for now, just '' because we will fill in later
        :returns: None
        """
        positions_counter = Counter()
        for person in self.people:
            for position_name in person.positions:
                positions_counter[position_name] += 1
        # TODO make the csv with the specified format
        with open('all_organizations.csv', mode='w') as csv_file:
            fieldnames = ['Raw Name', 'Count', 'Authoritative Name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for organization in positions_counter:
                writer.writerow({'Raw Name': organization, 'Count': positions_counter[
                    organization], 'Authoritative Name': ''})


    def merge_duplicates(self, print_merge_results_for_name='Dunn'):
        """
        Tries to merge all duplicates and only retain authoritative names.
        e.g. it will try to merge WL Dunn and William Dunn into Dunn, William L

        You can use print_merg_results_for_name to print out the merge results for one name for
        further inspection

        :param print_merge_results_for_name: str
        :return:
        """

        last_names = set()
        for person in self.people:
            last_names.add(person.last)

        for last_name in last_names:
            print(f"Merging: ", last_name)
            while True:
                last_names_dict = defaultdict(list)
                for person in self.people:
                    last_names_dict[person.last].append(person)

                finished = self.merge_last_name(last_names_dict, last_name)
                if finished:
                    if (
                        print_merge_results_for_name and
                        last_name.lower().find(print_merge_results_for_name.lower()) > -1
                    ):
                        print("\nSUMMARY")
                        for n in last_names_dict[last_name]:
                            print("\n", n.count, n, Counter(n.aliases).most_common(100))
                        print("\n")
                    break

    def merge_last_name(self, last_names_dict, last_name):
        """
        Iteratively tries to merge last names from the most common to the least common
        Returns true if it is finished,

        :param last_names_dict:
        :param last_name:
        :return:
        """

        # if only one name -> already finished
        if len(last_names_dict[last_name]) == 1:
            return True

        last_names_dict[last_name].sort(key=lambda x: x.count, reverse=True)

        for p1 in last_names_dict[last_name]:
            for p2 in last_names_dict[last_name]:

                if p1 == p2:
                    continue

                # if no first and middle name -> continue
                elif p1.first == '' and p1.middle == '':
                    continue
                elif p2.first == '' and p2.middle == '':
                    continue

                # if first and middle names match -> merge
                elif p1.first == p2.first and p1.middle == p2.middle:
                    self.merge_two_persons(p1, p2)
                    return False

                # if both have full first names and they don't match -> skip
                elif len(p1.first) > 2 and len(p2.first) > 2 and p1.first != p2.first:
                    continue

                # if both have full middle names and they don't match -> skip
                elif len(p1.middle) > 2 and len(p2.middle) > 2 and p1.middle != p2.middle:
                    continue

                # if initial of the first name is not the same -> skip
                elif p1.first and p2.first and p1.first[0] != p2.first[0]:
                    continue

                # if both have at least first and middle initials
                elif p1.first and p1.middle and p2.first and p2.middle:
                    if p1.first[0] != p2.first[0] or p1.middle[0] != p2.middle[0]:
                        continue

                    # if first and middle initials match -> merge
                    if p1.first[0] == p2.first[0] and p1.middle[0] == p2.middle[0]:
                        self.merge_two_persons(p1, p2)
                        return False    # we're not finished -> return False

                elif len(p1.first) == 1 and not p1.middle:
                    # TODO
                    continue
                elif len(p2.first) == 1 and not p2.middle:
                    # TODO
                    continue
                else:
                    continue

        # if no merges could be made return True to indicate that merge process is finished
        return True

    def merge_two_persons(self, person1, person2):

        new_p = person1.copy()

        for attr in ['first', 'middle']:
            if len(getattr(person2, attr)) > len(getattr(person1, attr)):
                setattr(new_p, attr, getattr(person2, attr))
        try:
            new_p.positions = person1.positions.union(person2.positions)
        except:
            embed()
        new_p.aliases = person1.aliases + person2.aliases
        new_p.count = person1.count + person2.count

        try:
            self.people.remove(person1)
            self.people.remove(person2)
            self.people.add(new_p)
        except KeyError:
            print('k')
            embed()

    def find_related_person(self, person: Person):
        pass

    def get_positions(self):
        positions = Counter()
        for person in self.people:
            for affiliation in person.positions:
                positions[affiliation] += 1

        return positions


def merge_names(name_file=Path('..', 'data', 'name_disambiguation', 'tobacco_names_raw_test.json')):

    with open(name_file, 'r') as infile:
        name_dict = json.load(infile)

    # add everyone to a PeopleDatabase
    people_db = PeopleDatabase()
    for name in name_dict:
        count_documents = name_dict[name]
        if name.lower().find('dunn') > -1:
            people_db.add_person_raw(name_raw=name, count=name_dict[name])

    # then merge the duplicate / similar names
    people_db.create_positions_csv()
    # people_db.merge_duplicates()


class TestNameParser(unittest.TestCase):
    def setUp(self):
        self.test_raw_names = {
            "TEAGUE CE JR": Person(last = "Teague", first = "C", middle = "E", positions = {"JR"}),
            "teague ce jr": Person(last="Teague", first="C", middle="E", positions={"JR"}),
            'Teague, J - BAT': Person(last='Teague', first='J', middle='', positions={'BAT'}),
            "Teague, Claude Edward, Jr., Ph.D.": Person(
                last="Teague", first="Claude", middle="Edward", positions={"JR, PHD"}
            ),


                               }
        self.default_raw_names = []

    def test_all_names(self):
        for name in self.test_raw_names:
            self.assertEqual(Person(name_raw = name), self.test_raw_names[name])


if __name__ == '__main__':
    a = Person(name_raw="TEAGUE CE J.R.")
    print("last", a.last, "first", a.first, "middle", a.middle)
    merge_names()
    # unittest.main()

