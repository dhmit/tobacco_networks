import copy
import json
import pickle
import re
import csv
from collections import Counter, defaultdict
from pathlib import Path
from IPython import embed
from nameparser import HumanName
from nameparser.config import CONSTANTS

from name_preprocessing import get_au_and_rc_by_document, get_clean_org_names

import unittest

CONSTANTS.titles.remove(*CONSTANTS.titles)


# dict that converts raw organization names to clean, official organization names
RAW_ORG_TO_CLEAN_ORG_DICT = get_clean_org_names()


class Person:
    """A Person object represents information of a person (possibly parsed from raw strings,
    or merged from different strings)

    Attributes:
        last (str): official parsed last name
        first (str): official parsed first name
        middle (str): official parsed middle name
        position (str): most likely organization of the person
        positions (Counter of str): counter of all parsed organizations/extra information (must
                                    be clean official org names; can be in lower case)
        aliases (list of str): list of raw names that correspond to the person
        count (int): number of times the alias appeared in the data
    """
    def __init__(self, name_raw=None, last='', first='', middle='', position='not calculated',
                 positions=None, aliases=None, count=1):
        """
        Returns a person object
        :param name_raw: raw string for the name (str)
        :param last: official parsed last name (if known) (str)
        :param first: official parsed first name (if known) (str)
        :param middle: official parsed middle name (if known) (str)
        :param position: official organization (if known; default is "not calculated") (str)
        :param positions: compilation of organizations/other information (if known) (Counter of str)
        :param aliases: list of raw strings that correspond to this person object (if known) (
        list of str)
        :param count: number of times the alias appeared in the data (int)
        """

        # if raw name is given, parse it using parse_raw_name() to get first, middle, last,
        # and positions
        if name_raw:
            first, middle, last, positions = self.parse_raw_name(name_raw, count)

        # initialize positions as an empty Counter if it is not given
        if positions is None:
            positions = Counter()

        # by default, the raw name is an alias of the person
        # (we're changing the first/middle names based on new information, so keeping the original
        # name as an alias is important
        if aliases is None:
            if name_raw is None:
                aliases = []
            else:
                aliases = [name_raw]

        # set last, first, middle, position, positions: all converted to upper case
        # set aliases and count
        self.last = last.upper()
        self.first = first.upper()
        self.middle = middle.upper()
        self.position = position
        # remove periods and convert to upper case
        if isinstance(positions, Counter):
            self.positions = positions
        else:
            # initialize positions as a Counter
            self.positions = Counter()
            for i in positions:
                cleaned = re.sub(r'\.', '', i)
                self.positions[cleaned.upper()] += count
        self.aliases = aliases
        self.count = count

    def __repr__(self):
        """
        Returns string representation of first, middle, last name, positions,
        and all aliases
        :return: str of first, middle, last, positions, aliases
        """
        s = f'{self.first} {self.middle} {self.last}'
        s = s + ", Position: " + str(self.positions) + ", Aliases: " + \
            str(self.aliases) + ", count: " + str(self.count)
        return s

    def __eq__(self, other):
        # TODO: figure out where this is actually called & what we should compare
        """
        Compares two person object using hash (which hashes the string of last, first, middle,
        position, positions, aliases, and count)
        :param other: another person object
        :return: bool (if two person objects are the same)
        """
        return \
            self.last == other.last and self.first == other.first\
            and self.middle == other.middle and self.position == other.position\
            and self.positions == other.positions and self.aliases == other.aliases

    def copy(self):
        """
        Copies a person object
        :return: a copied person object
        """
        return Person(last=self.last, first=self.first, middle=self.middle,
                      position=self.position,
                      positions=copy.deepcopy(self.positions),
                      aliases=copy.deepcopy(self.aliases), count=self.count)

    def __hash__(self):
        """
        Hashes the person
        :return: hash (int)
        """
        return hash(f'{self.last} {self.first} {self.middle} {self.positions} {self.aliases}')

    def stemmed(self):
        """
        Returns only the official name ("LAST FIRST MIDDLE") of the person
        :return: str of official name
        """
        return f'{self.last} {self.first} {self.middle}'

    def set_likely_position(self):
        """
        Calculates and sets position as the organization with the highest number of count
        :return: None
        """
        likely_position = self.positions.most_common(1)[0][0]
        self.position = likely_position

    @staticmethod
    def parse_raw_name(name_raw: str, count: int) -> (str, str, str, Counter):
        """
        Parses a (usually messy) raw name and returns
        first, middle, last names and a set of extracted positions

        :param name_raw: str
        :param count: int
        :return: str, str, str, set
        """

        # remove privlog info, e.g. 'Temko, Stanley L [Privlog:] TEMKO,SL'. It confuses
        # the name parser
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
            extracted_positions = [extracted_position.strip()]
        else:
            extracted_positions = []

        # extract positions in parens e.g. Henson, A (Chadbourne & Park)
        paren_positions = re.findall(r'\([^(]+\)', name_raw)
        for position in paren_positions:
            extracted_positions.append(position.strip(',#() '))
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
                extracted_positions.append(extracted_institution.group().strip(',#() '))
                name_raw = name_raw[:name_raw.find(extracted_institution.group())]
        # remove #
        name_raw = name_raw.strip("#").strip()

        # DUNN-W -> Dunn W
        if name_raw[-2] == '-':
            name_raw = name_raw[:-2] + " " + name_raw[-1:]

        # DUNN-WL -> DUNN WL
        if len(name_raw) > 2 and name_raw[-3] == '-':
            name_raw = name_raw[:-3] + " " + name_raw[-2:]

        # if there is a special character, take out the word surrounding it (i.e. no space or
        # comma) into extracted_positions (since it is unlikely to be in the name)
        match_non_alpha = r'[^ ,]*[^A-Z ,\-\(\)\.][^ ,]*'
        while re.search(match_non_alpha, name_raw, re.IGNORECASE):
            non_alpha = re.search(match_non_alpha, name_raw, re.IGNORECASE)
            extracted_positions.append(non_alpha.group())
            name_raw = \
                name_raw[:name_raw.find(non_alpha.group())] + name_raw[name_raw.find(
                    non_alpha.group()) + len(non_alpha.group()):]

        for raw_org in RAW_ORG_TO_CLEAN_ORG_DICT:
            if raw_org in name_raw:
                extracted_positions.append(RAW_ORG_TO_CLEAN_ORG_DICT[raw_org])
                name_raw = name_raw[:name_raw.find(raw_org)] + name_raw[name_raw.find(
                    raw_org) + len(raw_org):]


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

        # should we keep this?
        # if ' ' in name.last:
        #     splitname = name.last.split(' ')
        #     name.last = splitname[0]
        #     name.last = max(splitname, key=lambda name: len(name))

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
            extracted_positions.append(name.suffix)

        # map organization names to clean official names (if they are in the dict) using
        # RAW_ORG_TO_CLEAN_ORG_DICT
        for i in range(len(extracted_positions)):
            if extracted_positions[i] in RAW_ORG_TO_CLEAN_ORG_DICT:
                extracted_positions[i] = RAW_ORG_TO_CLEAN_ORG_DICT[extracted_positions[i]]

        # convert mapped positions into a counter
        result_positions = Counter()
        for position in extracted_positions:
            cleaned = re.sub(r'\.', '', position)
            result_positions[cleaned.upper()] += count

        print(name.first, name.middle, name.last, result_positions)
        return name.first, name.middle, name.last, result_positions


# PeopleDatabase object
class PeopleDatabase:
    """A PeopleDatabase object represents the collection of person objects
    and contains functions that merge person objects

    Attributes:
        people (set): collection of all person objects in the database
    """
    def __init__(self):
        """
        Intiailizes an empty PeopleDatabase
        """
        self.people = set()

    def add_person_raw(self, name_raw: str, count=1):
        """
        Adds Person object to the database from a raw name string & count
        :param name_raw: raw name (str)
        :param count: number of times name_raw appeared (int)
        :return: None
        """

        try:
            new_p = Person(name_raw=name_raw, count=count)
            self.people.add(new_p)
        except IndexError:
            print(f"Could not parse name_raw {name_raw} to Person.")

    def __len__(self):
        """
        Returns the number of people in the database
        :return: int (length of self.people)
        """
        return len(self.people)

    def __eq__(self, other):
        """
        Compares two PeopleDatabase objects
        :param other: another PeopleDatabase object
        :return: bool (if the people sets are the same)
        """
        hash1 = []
        hash2 = []
        for person in self.people:
            hash1.append(hash(person))
        for person in other.people:
            hash2.append(hash(person))
        return sorted(hash1) == sorted(hash2)

    def __repr__(self):
        """
        Returns string representation of the database: number of people in the database,
        and string representation of each person
        :return: str
        """
        return f"<PeopleDatabase with {len(self.people)} people:\n " \
               f"{[i for i in self.people]}>"

    def get_alias_to_person_dict(self):
        """
        Returns a dict that corresponds aliases to person objects
        :return: dict
        """
        alias_to_person = {}
        for person in self.people:
            for alias in person.aliases:
                alias_to_person[alias] = person
        return alias_to_person

    def store_to_disk(self, file_path: Path):
        """
        Stores a people db to disk as a pickle file
        :param file_path: Path
        :return:
        """

        with open(str(file_path), 'wb') as outfile:
            pickle.dump(self, outfile)

    def load_from_disk(self, file_path: Path):
        """
        Load a people db from a pickle file
        :param file_path:
        :return:
        """

        with open(str(file_path), 'rb') as infile:
            loaded_db = pickle.load(infile)
            self.people = loaded_db.people

    # TODO: Figure out if we still need this / add authoritative name
    def create_positions_csv(self):
        """
        Makes a Counter of all positions appearing in db,
        Translates this info into a CSV,
        1st Col = raw name
        2nd Col = count in Counter
        3rd Col = authoritative name – for now, just '' because we will fill in later
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
                authoritative_name = "-"
                if organization in RAW_ORG_TO_CLEAN_ORG_DICT:
                    authoritative_name = RAW_ORG_TO_CLEAN_ORG_DICT[organization]
                writer.writerow({'Raw Name': organization, 'Count': positions_counter[
                    organization], 'Authoritative Name': authoritative_name})

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

        for last_name in sorted(last_names):
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
        """
        Create a new person by merging data of person1 and person2, and replace person1 and
        person2 in the people db with the new person
        :param person1: a person object
        :param person2: another person object to be merged
        :return:
        """
        new_p = person1.copy()

        for attr in ['first', 'middle']:
            if len(getattr(person2, attr)) > len(getattr(person1, attr)):
                setattr(new_p, attr, getattr(person2, attr))
        try:
            new_p.positions = person1.positions + person2.positions
        except TypeError:
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

    def set_people_position(self):
        """
        For each Person object in the people db, set its position as the most appeared
        organization name
        :return:
        """
        for person in self.people:
            person.set_likely_position()


def merge_names_from_file(name_file=Path('..', 'data', 'name_disambiguation',
                                         'tobacco_names_raw_test_small.json')):
    """
    Creates a people db from reading json file (dict of raw names and counts) and merges people
    in it. Stores people db in a pickle file
    :param name_file:
    :return:
    """

    with open(name_file, 'r') as infile:
        name_dict = json.load(infile)

    import time
    s = time.time()

    # add everyone to a PeopleDatabase
    people_db = PeopleDatabase()
    for name in name_dict:
        if name_dict[name] >= 3:
            people_db.add_person_raw(name_raw=name, count=name_dict[name])

    print("Length: ", len(people_db))

    # then merge the duplicate / similar names
    people_db.create_positions_csv()
    people_db.merge_duplicates()

    people_db.store_to_disk(Path('names_db_3.pickle'))
    print("Merging names took", time.time() - s)

#    with open('alias_to_name.json', 'w') as outfile:
#        json.dump(people_db.get_alias_to_name(), outfile)


class TestNameParser(unittest.TestCase):
    """Tests name parsing (parse_raw_name) of the Person class
    Attributes:
        test_raw_names: dict that corresponds raw names (str) to the expected Person object
    """
    # TODO: fix it so that all tests run even if the first assertion fails
    def setUp(self):
        self.test_raw_names = {
            # test Person constructor: use list as positions
            "TEAGUE CE JR": Person(last="Teague", first="C", middle="E", positions=["JR"],
                                   aliases=["TEAGUE CE JR"]),
            # test Person constructor: use Counter as positions
            "teague ce jr": Person(last="Teague", first="C", middle="E", positions=Counter([
                "JR"]), aliases=["teague ce jr"]),
            'Teague, J - BAT': Person(last='Teague', first='J', middle='',
                                      positions={'British American Tobacco'},
                                      aliases=['Teague, J - BAT']),
            # TODO: should be "JR", "PHD"
            "Teague, Claude Edward, Jr., Ph.D.": Person(
                last="Teague", first="Claude", middle="Edward", positions={"JR, PHD"},
                aliases=["Teague, Claude Edward, Jr., Ph.D."]
            ),
            "BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS GENERAL": Person(
                last="Baker", first="T", middle="E",
                positions={"NATIONAL ASSOCIATION OF ATTORNEYS GENERAL"},
                aliases=["BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS GENERAL"]
            ),
            # specify positions: test to make sure Counter can handle no data
            "BAKER-cj": Person(last="Baker", first="C", middle="J", positions={},
                               aliases=["BAKER-cj"]),
            # not specify positions: test to make sure Person constructor can handle no data
            "Baker, JR": Person(last="Baker", first="J", middle="R", aliases=["Baker, JR"]),
            "DUNN WL #": Person(last="Dunn", first="W", middle="L", aliases=["DUNN WL #"]),
            "Dunn, W. L.": Person(last="Dunn", first="W", middle="L", aliases=["Dunn, W. L."]),
            "TEMKO SL, COVINGTON AND BURLING": Person(last="Temko", first="S", middle="L",
                                                      positions=["COVINGTON AND BURLING"],
                                                      aliases=["TEMKO SL, COVINGTON AND BURLING"],
                                                      ),
            "Temko, Stanley L [Privlog:] TEMKO,SL": Person(
                last="Temko", first="Stanley", middle="L",
                aliases=["Temko, Stanley L [Privlog:] TEMKO,SL"]
            ),
            "Temko-SL, Covington & Burling": Person(
                last="Temko", first="S", middle="L", positions=["Covington & Burling"],
                aliases=["Temko-SL, Covington & Burling"]
            ),
            "HENSON, A. (AMERICAN SENIOR VICE PRESIDENT AND GENERAL COUNSEL)": Person(
                last="Henson", first="A", middle="",
                positions=["AMERICAN SENIOR VICE PRESIDENT AND GENERAL COUNSEL"],
                aliases=["HENSON, A. (AMERICAN SENIOR VICE PRESIDENT AND GENERAL COUNSEL)"]
            ),
            "HENSON, A. (CHADBOURNE, PARKE, WHITESIDE & WOLFF, AMERICAN OUTSIDE COUNSEL) " +
            "(HANDWRITTEN NOTES)": Person(
                last="Henson", first="A", middle="",
                positions=["CHADBOURNE, PARK, WHITESIDE & WOLFF", "@skip@"],
                aliases=["HENSON, A. (CHADBOURNE, PARKE, WHITESIDE & WOLFF, AMERICAN OUTSIDE " +
                         "COUNSEL) (HANDWRITTEN NOTES)"]
            ),
            "Holtzman, A.,  Murray, J. ,  Henson, A. ,  Pepples, E. ,  Stevens, A. ,  Witt, S.":
            Person(last="Holtzman", first="A", middle="", positions=[],
                   aliases=["Holtzman, A.,  Murray, J. ,  Henson, A. ,  " +
                            "Pepples, E. ,  Stevens, A. ,  Witt, S."]),
            "Holtz, Jacob, Jacob & Medinger": Person(
                last="Holtz", first="Jacob", middle="", positions=["JACOB & MEDINGER"],
                aliases=["Holtz, Jacob, Jacob & Medinger"]
            ),
            "PROCTOR DF, JOHNS HOPKINS SCHOOL OF HYGIENE": Person(
                last="Proctor", first="D", middle="F",
                positions=["JOHNS HOPKINS SCHOOL OF HYGIENE"],
                aliases=["PROCTOR DF, JOHNS HOPKINS SCHOOL OF HYGIENE"]
            ),
            "Smith, Andy B, J.R.": Person(
                last="Smith", first="Andy", middle="B", positions=["JR"],
                aliases=["Smith, Andy B, J.R."]
            ),
            "D Cantrell, B&W": Person(
                last="Cantrell", first="D", middle="", positions=["BROWN & WILLIAMSON"],
                aliases=["D Cantrell, B&W"]
            ),
            # TODO: would be nice to pass this one
            "A B Cantrell, BW": Person(
                last="Cantrell", first="A", middle="B", positions=["BROWN & WILLIAMSON"],
                aliases=["A B Cantrell, BW"]
            )
        }

    # Not sure what the correct parsing is!
    # This one breaks. But I don't think it can be avoided.
    # >> > n = Person('Holtz, Jacob Alexander, Jacob & Medinger')
    # >> > n.last, n.first, n.middle, " ".join(n.positions).upper()
    # ('Holtz', '', '', 'JACOB ALEXANDER, JACOB & MEDINGER')

    def test_all_names(self):
        """
        Iterates over all test names in self.test_raw_names and check if the Person object parsed
        from Person class matches the expected Person object
        :return:
        """
        for name in self.test_raw_names:
            print(f"Expected: {str(self.test_raw_names[name])}")
            print(f"Parsed: {str(Person(name_raw=name))}")
            self.assertEqual(self.test_raw_names[name], Person(name_raw=name))



class TestPeopleDB(unittest.TestCase):
    def setUp(self):
        self.people_db = PeopleDatabase()
        for name in ['Dunn, WL', 'Garcia, Raquel', 'Risi, Stephan']:
            self.people_db.add_person_raw(name, 1)

    def test_pickle(self):
        """
        Test if pickling works
        """
        self.people_db.store_to_disk(Path('test.pickle'))
        loaded_db = PeopleDatabase()
        loaded_db.load_from_disk(Path('test.pickle'))
        self.assertEqual(self.people_db, loaded_db)

    def test_add_au_and_rc_org(self):
        add_au_and_rc_org(self.people_db, Path('..', 'data', 'name_disambiguation',
                                               'test_docs.csv'))

        expected_people_db = PeopleDatabase()
        raquel = Person('Garcia, Raquel')
        raquel.positions = Counter(["British American Tobacco"])
        expected_people_db.people.add(raquel)

        dunn = Person('Dunn, WL')
        dunn.positions = Counter(["British American Tobacco"])
        expected_people_db.people.add(dunn)

        stephan = Person('Risi, Stephan')
        stephan.positions = Counter(["Philip Morris", "Philip Morris"])
        expected_people_db.people.add(stephan)

        print(self.people_db)
        print(expected_people_db)

        self.assertEqual(self.people_db, expected_people_db)


def add_au_and_rc_org(db_to_add, path):
    """
    Input are a people database and a path to a document
    Returns None

    For each document belonging to a certain company,
    finds Person that that document author alias maps to,
    and adds that company to the position counter of that Person

    :param db_to_add: a PeopleDatabase, path: path to authors/orgs document
    :param path: file path to the docs csv file that includes au_org & rc_org
    :return: None
    """

    alias_to_person_dict = db_to_add.get_alias_to_person_dict()

    def update_au_and_rc_positions(db_current, au_or_rc, relevant_dicts):
        """
        Goes through documents and updates authors/recipients' positions
        based on organization associated with document

        Adds people to db_current if their alias is associated with a doc but is not in
        db_current yet

        Ignores:
            organizations not in RAW_ORG_TO_CLEAN_ORG_DICT
            docs with more than 1 organization
            docs with more than 4 recipients
            docs with no people associated with them

        :param db_current: People Database
        :param au_or_rc: string ('au' or 'rc')– specifies whether we're looking at authors or
        recipients
        :param relevant_dicts: 2 item list, 1st = dict with authors and organizations, by doc,
        2nd = dict of recipients and organizations by doc.
        :return: None
        """
        if au_or_rc == 'au':
            relevant_person = 'au_person'
            relevant_org = 'au_org'
        else:
            relevant_person = 'rc_person'
            relevant_org = 'rc_org'

        for doc in relevant_dicts:
            orgs = set()
            for org in doc[relevant_org]:
                if org not in RAW_ORG_TO_CLEAN_ORG_DICT:
                    continue
                else:
                    orgs.add(RAW_ORG_TO_CLEAN_ORG_DICT[org])

            if len(orgs) != 1:
                continue
            else:
                org = list(orgs)[0]
                aliases = doc[relevant_person]
                aliases.extend(doc[au_or_rc])
                if au_or_rc == 'rc' and len(aliases) >= 5:
                    continue
                if not aliases:
                    continue
                for alias in aliases:
                    if alias not in alias_to_person_dict:
                        db_current.add_person_raw(alias)
                    else:
                        alias_to_person_dict[alias].positions[org] += 1

    au_dicts, rc_dicts = get_au_and_rc_by_document(path)
    update_au_and_rc_positions(db_to_add, 'au', au_dicts)
    update_au_and_rc_positions(db_to_add, 'rc', rc_dicts)


if __name__ == '__main__':
    # db = PeopleDatabase()
    # db.load_from_disk(Path("names_db_10.pickle"))
    # add_au_and_rc_org(db, Path('..', 'data', 'name_disambiguation', 'dunn_docs.csv'))
    # db.merge_duplicates()
    # print(db)

    merge_names_from_file()
    # db = PeopleDatabase()
    # db.load_from_disk("d_names_db.pickle")
    # print(add_au_and_rc_org(db))
