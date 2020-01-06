"""
The People Database provides a class to add and merge persons
"""

import copy
import csv
import itertools
import pickle
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from nameparser.config import CONSTANTS  # pylint: disable=C0411

from name_disambiguation.clean_org_names import RAW_ORG_TO_CLEAN_ORG_DICT
from name_disambiguation.config import COMPANY_ABBREVIATIONS_TO_SKIP
from name_disambiguation.person import Person

CONSTANTS.titles.remove(*CONSTANTS.titles)


class PeopleDatabase:
    """
    A PeopleDatabase object represents the collection of person objects
    and contains functions that merge person objects
    Attributes:
        people (set): collection of all person objects in the database
    """
    def __init__(self):
        """
        Intiailizes an empty PeopleDatabase
        """
        self.people = set()
        self._alias_to_person_dict = {}
        self.raw_org_to_clean_org_dict = RAW_ORG_TO_CLEAN_ORG_DICT.copy()

    def add_person_raw(self, name_raw: str, count=1, position=None):
        """
        Adds Person object to the database from a raw name string & count
        :param name_raw: raw name (str)
        :param count: number of times name_raw appeared (int)
        :return: None
        """
        try:
            if position:
                if isinstance(position, str):
                    positions = Counter(position)
                elif isinstance(position, Counter):
                    positions = position
                else:
                    raise ValueError("position has to be a string or Counter")
            else:
                positions = Counter()

            new_p = Person(name_raw=name_raw, count=count, positions=positions)

            # if the raw name is already in the people_db, merge the entries
            existing_p = self.get_person_from_alias(name_raw)
            if existing_p:
                # remove person temporarily as the hash value will change with the updates
                # making it impossible to remove later
                self.people.remove(existing_p)
                existing_p.positions += new_p.positions
                existing_p.aliases += new_p.aliases
                existing_p.count += new_p.count

                self.add_alias_to_alias_to_person_dict(name_raw, existing_p)
                if not self.get_person_from_alias(existing_p.full_name):
                    self.add_alias_to_alias_to_person_dict(existing_p.full_name, existing_p)
                self.people.add(existing_p)

                # add any new organizations to the raw_org_to_clean_dict
                for pos in existing_p.positions:
                    if not pos in self.raw_org_to_clean_org_dict:
                        self.raw_org_to_clean_org_dict[pos] = pos

            else:
                self.people.add(new_p)
                self.add_alias_to_alias_to_person_dict(name_raw, new_p)
                if not self.get_person_from_alias(new_p.full_name):
                    self.add_alias_to_alias_to_person_dict(new_p.full_name, new_p)
                # add any new organizations to the raw_org_to_clean_dict
                for pos in new_p.positions:
                    if not pos in self.raw_org_to_clean_org_dict:
                        self.raw_org_to_clean_org_dict[pos] = pos

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
        for person in sorted(list(self.people)):
            hash1.append(hash(person))
        for person in sorted(list(other.people)):
            hash2.append(hash(person))
        return sorted(hash1) == sorted(hash2)

    def __repr__(self):
        """
        Returns string representation of the database: number of people in the database,
        and string representation of each person
        :return: str
        """
        return f"<PeopleDatabase with {len(self.people)} people:\n {self.people}>"

    def copy(self):
        """
        Copies a people_db object
        :return: a copied people_db object
        """
        people_db_copy = PeopleDatabase()
        people_db_copy.people = copy.deepcopy(self.people)
        return people_db_copy

    @property
    def counter(self):
        """

        :return:
        """
        person_counter = Counter()
        for person in self.people:
            person_counter[person] = person.count
        return person_counter


    def generate_alias_to_person_dict(self):
        """
        Generates a the _alias_to_person_dict that corresponds aliases to person objects
        :return: dict
        """

        for person in self.people:
            for alias in person.aliases.keys():
                self.add_alias_to_alias_to_person_dict(alias, person)
                if not self.get_person_from_alias(person.full_name):
                    self.add_alias_to_alias_to_person_dict(person.full_name, person)

        # alias_to_person = {}
        # for person in self.people:
        #     for alias in person.aliases:
        #         alias_to_person[alias] = person
        # return alias_to_person

    def store_to_disk(self, file_path: Path):
        """
        Stores a people db to disk as a pickle file
        :param file_path: Path for storing pickle file
        :return:
        """

        with open(str(file_path), 'wb') as outfile:
            pickle.dump(self, outfile)

    def load_from_disk(self, file_path: Path):
        """
        Load a people db from a pickle file
        :param file_path: Path of pickle file
        :return:
        """


        with open(str(file_path), 'rb') as infile:
            loaded_db = pickle.load(infile)

            self.people = set()
            self._alias_to_person_dict = {}
            self.raw_org_to_clean_org_dict = RAW_ORG_TO_CLEAN_ORG_DICT
            for person in loaded_db.people:

                # our main person db has some company accounts in there -> delete
                add_person = True
                for alias in person.aliases.keys():
                    if (
                            alias.lower().replace(' ', '') in COMPANY_ABBREVIATIONS_TO_SKIP or
                            person.full_name.lower().replace(' ', '') in
                            COMPANY_ABBREVIATIONS_TO_SKIP
                    ):
                        add_person = False
                        break

                # for position in person.positions:
                #     if position not in self.raw_org_to_clean_org_dict:
                #         self.raw_org_to_clean_org_dict[position] = position

                if add_person:
                    self.people.add(person)


            self.generate_alias_to_person_dict()
            self.add_manually_merged_names()
            self.generate_alias_to_person_dict()


    def add_alias_to_alias_to_person_dict(self, alias: str, person: Person): # pylint: disable=C0103
        """
        Adds an alias to the _alias_to_person_dict, making the alias lower case and removing
        white space
        so far, adding and looking up has been done directly with the dict but capitalization is
        inconsistent, so we missed some important matches.

        :param alias: str
        :param person: Person
        :return:
        """
        self._alias_to_person_dict[alias.lower()] = person

    def remove_alias_to_alias_to_person_dict(self, alias: str):     # pylint: disable=C0103
        """
        Removes an alias from the alias_to_person_dict

        :param alias: str
        :return:
        """

        del self._alias_to_person_dict[alias.lower()]

    def get_person_from_alias(self, alias: str):
        """
        loads a Person object by alias
        If it doesn't find a person under the alias, returns None

        :param alias: str
        :return:
        """

        alias = alias.lower()
        if alias in self._alias_to_person_dict:
            return self._alias_to_person_dict[alias]
        else:
            return None


    def add_manually_merged_names(self):
        """
        The automatic merging works reasonably well but in some cases, it is worth to merge
        people by hand.
        These manual merges are defined in MANUALLY_MERGED_NAMES in config.py
        This script tries to add them
        """

        from name_disambiguation.config import MANUALLY_MERGED_NAMES

        for person in MANUALLY_MERGED_NAMES:

            for i in range(len(person['aliases_to_merge']) - 1):
                alias1 = person['aliases_to_merge'][i]
                alias2 = person['aliases_to_merge'][i + 1]

                person1 = self.get_person_from_alias(alias1)
                person2 = self.get_person_from_alias(alias2)

                if person1 and person2:
                    if person1 != person2:
                        self.merge_two_persons(person1, person2, person['authoritative_name'])
                    else:
                        # temporarily remove person1 because we're messing with the hash key
                        # and couldn't remove it later
                        self.people.remove(person1)
                        person1.first = person['authoritative_name']['first']
                        person1.middle = person['authoritative_name']['middle']
                        person1.last = person['authoritative_name']['last']
                        if 'affiliation' in person['authoritative_name']:
                            person1.positions[person['authoritative_name']['affiliation']] = 9999
                        for alias in person1.aliases:
                            self.add_alias_to_alias_to_person_dict(alias, person1)
                        self.add_alias_to_alias_to_person_dict(person1.full_name, person1)
                        self.people.add(person1)

                else:
                    # print(f'Could not find {alias1} or {alias2} in people db')
                    pass

    def create_positions_csv(self, out_file=Path('..', 'data', 'name_disambiguation',
                                                 'all_organizations.csv')):
        """
        Makes a Counter of all positions appearing in db,
        Translates this info into a CSV,
        1st Col = raw name of organization
        2nd Col = count in Counter
        3rd Col = clean authoritative name
        :param out_file: Path for output csv file
        :returns: None
        """
        positions_counter = Counter()
        for person in self.people:
            for position_name in person.positions:
                positions_counter[position_name] += 1
        with open(out_file, mode='w') as csv_file:
            fieldnames = ['Raw Name', 'Count', 'Authoritative Name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for organization in positions_counter:
                authoritative_name = "-"
                if organization in self.raw_org_to_clean_org_dict:
                    authoritative_name = self.raw_org_to_clean_org_dict[organization]
                writer.writerow({'Raw Name': organization, 'Count': positions_counter[
                    organization], 'Authoritative Name': authoritative_name})

    def merge_duplicates(self, print_merge_results_for_name='Dunn', manual_merge=False):
        """
        Tries to merge all duplicates and only retain authoritative names.
        e.g. it will try to merge WL Dunn and William Dunn into Dunn, William L
        You can use print_merg_results_for_name to print out the merge results for one name for
        further inspection

        if manual_merge = True, user will be prompted to decide for all last names if they should
        be merged manually. useful for small networks for display purposes.

        :param print_merge_results_for_name: str
        :param manual_merge: bool
        :return:
        """

        last_names = set()
        for person in self.people:
            last_names.add(person.last)

        for last_name in sorted(last_names):
            while True:
                last_names_dict = defaultdict(list)
                for person in self.people:
                    last_names_dict[person.last].append(person)

                finished = self.merge_last_name(last_names_dict, last_name)
                if finished:
                    if (
                            print_merge_results_for_name and
                            len(last_names_dict[last_name]) > 5
                            # last_name.lower().find(print_merge_results_for_name.lower()) > -1
                    ):
                        print("\nSUMMARY")
                        for name in last_names_dict[last_name]:
                            print("\n", name.count, name, name.aliases.most_common(100))
                        print("\n")
                    break

        if manual_merge:
            self.manually_merge_db()

    def manually_merge_db(self):
        """
        Manually merge the names in the database.
        Allows user to merge, for example, "Kornegay, Horace A." with "Kornegay H.", which the
        automated merger does not do.
        Relies on user input -> use only for small people databases.

        :return:
        """

        last_names = set()
        for person in self.people:
            last = person.last.upper().replace('*', '')
            last_names.add(last)

        for last_name in sorted(last_names):
            self.manually_merge_last_name(last_name)

    def manually_merge_last_name(self, last_name):
        """
        manually merges everyone in the database with a given last name.

        :param last_name: str
        :return:
        """

        while True:
            candidates = []
            for person in self.people:
                if person.last.upper().replace('*', '') == last_name:
                    candidates.append(person)

            if len(candidates) == 1:
                return

            breaking = True
            for combination in itertools.combinations(candidates, 2):

                person1, person2 = combination
                if person1.first and person2.first and person1.first[0] != person2.first[0]:
                    print('skipping because of different first names', person1.full_name,
                          person2.full_name)
                    continue

                print(f'\n\nMerge candidate: {person1.full_name} <-> {person2.full_name}')
                print("\n", person1)
                print("\n", person2)

                selection = input("Should these 2 people get merged? (y/n):   ")
                # selection = 'y'
                if selection == 'y':
                    new_p = self.merge_two_persons(person1, person2)
                    print("new", new_p)
                    breaking = False
                    break

                if selection == 'n':    # pylint: disable=R1703
                    breaking = True
                else:
                    breaking = False

            if breaking:
                break




    def merge_last_name(self, last_names_dict, last_name):
        """
        Iteratively tries to merge last names from the most common to the least common
        Returns true if it is finished,
        :param last_names_dict: dict mapping last_name strings to list of
        :param last_name:
        :return:
        """

        # if only one name -> already finished
        if len(last_names_dict[last_name]) == 1:
            return True

        last_names_dict[last_name].sort(key=lambda x: x.count, reverse=True)

        for person1_idx, person1 in enumerate(last_names_dict[last_name]):
            for person2_idx, person2 in enumerate(last_names_dict[last_name]):

                # p1/2_idx indicate the index of the person. If they are the same, we are dealing
                # with the same person and should skip.
                if person1_idx == person2_idx:                                    # pylint: disable=R1724
                    continue

                # If p1 and person2 share at least one alias, we can merge them
                # the primary use of this is to merge cases where the same author was added
                # multiple times
                elif len(set(person1.aliases).intersection(set(person2.aliases))) > 0:
                    self.merge_two_persons(person1, person2)
                    return False


                # if no first and middle name -> continue
                elif person1.first == '' and person1.middle == '':
                    continue
                elif person2.first == '' and person2.middle == '':
                    continue

                # if first and middle names match -> merge
                elif person1.first == person2.first and person1.middle == person2.middle:
                    self.merge_two_persons(person1, person2)
                    return False

                # if both have full first names and they don't match -> skip
                elif (
                        len(person1.first) > 2 and len(person2.first) > 2 and
                        person1.first != person2.first
                ):
                    continue

                # if both have full middle names and they don't match -> skip
                elif (
                        len(person1.middle) > 2 and len(person2.middle) > 2 and
                        person1.middle != person2.middle
                ):
                    continue

                # if initial of the first name is not the same -> skip
                elif person1.first and person2.first and person1.first[0] != person2.first[0]:
                    continue

                # if both have at least first and middle initials
                elif person1.first and person1.middle and person2.first and person2.middle:
                    if (
                            person1.first[0] != person2.first[0] or
                            person1.middle[0] != person2.middle[0]
                    ):
                        continue

                    # if first and middle initials match -> merge
                    if (
                            person1.first[0] == person2.first[0] and
                            person1.middle[0] == person2.middle[0]
                    ):
                        self.merge_two_persons(person1, person2)
                        return False    # we're not finished -> return False

                elif len(person1.first) == 1 and not person1.middle:
                    # TODO
                    continue
                elif len(person2.first) == 1 and not person2.middle:
                    # TODO
                    continue
                else:
                    continue

        # if no merges could be made return True to indicate that merge process is finished
        return True

    def merge_two_persons(self, person1, person2, authoritative_name=None):
        """
        Create a new person by merging data of person1 and person2, and replace person1 and
        person2 in the people db with the new person
        :param person1: a person object
        :param person2: another person object to be merged
        :return:
        """
        # print("\n\nmerging\n", person1, "\n", person2)

        new_p = person1.copy()

        if authoritative_name:
            new_p.last = authoritative_name['last']
            new_p.first = authoritative_name['first']
            new_p.middle = authoritative_name['middle']

            # TODO: create implementation without ugly default value
            if 'affiliation' in authoritative_name:
                new_p.positions[authoritative_name['affiliation']] = 9999
        else:

            for attr in ['first', 'middle']:
                if (
                        len(getattr(person2, attr)) > len(getattr(person1, attr)) or
                        # no first or middle name should have a forward slash (e.g. "dk/shook")
                        # in that case, take the other name
                        getattr(person1, attr).find('/') > -1
                ):
                    setattr(new_p, attr, getattr(person2, attr))

        self.remove_alias_to_alias_to_person_dict(person1.full_name)
        if person1.full_name.lower() != person2.full_name.lower():
            try:
                self.remove_alias_to_alias_to_person_dict(person2.full_name)
            except KeyError:
                print(f"key error trying to remove {person2.full_name}. This can happen when "
                      f"merging many very similar names but might be worth investigating.")


        new_p.positions = person1.positions + person2.positions
        if authoritative_name and 'affiliation' in authoritative_name:
            new_p.positions[authoritative_name['affiliation']] = 9999

        new_p.aliases = person1.aliases + person2.aliases
        new_p.count = person1.count + person2.count

        for alias in new_p.aliases:
            self.add_alias_to_alias_to_person_dict(alias, new_p)
        self.add_alias_to_alias_to_person_dict(new_p.full_name, new_p)

        self.people.remove(person1)
        self.people.remove(person2)
        self.people.add(new_p)

        return new_p


class TestPeopleDB(unittest.TestCase):
    """
    Test cases for the people db
    """
    def setUp(self):
        self.people_db = PeopleDatabase()
        for initial_name in ['Dunn, WL', 'Garcia, Raquel', 'Risi, Stephan', 'Dunn, WL',
                             'Dunn, William L', 'Garcia, Raquel']:
            self.people_db.add_person_raw(initial_name, 1)

    def test_pickle(self):
        """
        Test if pickling works
        """
        self.people_db.store_to_disk(Path('..', 'data', 'name_disambiguation',
                                          'test_peopledb.pickle'))
        loaded_db = PeopleDatabase()
        loaded_db.load_from_disk(Path('..', 'data', 'name_disambiguation',
                                      'test_peopledb.pickle'))
        self.assertEqual(self.people_db, loaded_db)

    def test_merge1(self):
        """
        Test people_db merge 1
        """

        self.people_db.merge_duplicates()
        self.assertEqual(len(self.people_db), 3)

        alias_set = len(set(self.people_db._alias_to_person_dict.values())) # pylint: disable=W0212
        self.assertEqual(len(self.people_db), alias_set)

    def test_merge2(self):
        """
        Test people_db merge 2
        """

        people_db_test = PeopleDatabase()
        for name in ['DUNN,W', 'DUNN,WL', 'DUNN,WL JR', 'DUNN, W. L.', 'Dunn, FW,'
                     'Dunn, William L', 'Dunn,WL', 'DUNN,WL Jr', 'DUNN, WL', 'Dunn, Frank',
                     'Dunn, Frank W']:
            people_db_test.add_person_raw(name, 1)
        people_db_test.merge_duplicates()
        self.assertEqual(len(people_db_test), 4)
        alias_set = len(set(self.people_db._alias_to_person_dict.values()))  # pylint: disable=W0212
        self.assertEqual(len(people_db_test), alias_set)


if __name__ == '__main__':
    unittest.main()
