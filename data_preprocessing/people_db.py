"""
The People Database provides a class to add and merge persons
"""

import csv
import pickle
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from IPython import embed
from nameparser.config import CONSTANTS  # pylint: disable=C0411
from clean_org_names import RAW_ORG_TO_CLEAN_ORG_DICT
from person import Person

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
        return f"<PeopleDatabase with {len(self.people)} people:\n {self.people}>"

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
            self.people = loaded_db.people

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
                        for name in last_names_dict[last_name]:
                            print("\n", name.count, name, Counter(name.aliases).most_common(100))
                        print("\n")
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

        for p1 in last_names_dict[last_name]:           # pylint: disable=C0103
            for p2 in last_names_dict[last_name]:       # pylint: disable=C0103

                if p1 == p2:                            # pylint: disable=R1724
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

    def set_people_position(self, official_org=True):
        """
        For each Person object in the people db, set its position as the most appeared
        organization name
        If official_org=True, only consider most common organization that is in
        RAW_ORG_TO_CLEAN_ORG_DICT (if none of the raw orgs are in the dict, return the most common)
        :return:
        """
        for person in self.people:
            person.set_likely_position(official_org)


class TestPeopleDB(unittest.TestCase):
    """
    Test cases for the people db
    """
    def setUp(self):
        self.people_db = PeopleDatabase()
        for name in ['Dunn, WL', 'Garcia, Raquel', 'Risi, Stephan']:
            self.people_db.add_person_raw(name, 1)

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
