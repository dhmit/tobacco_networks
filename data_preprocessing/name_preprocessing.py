"""
Contains helper functions:
Create and pickles a People Database from CSV
Extract author and recipient aliases from CSV with documents info
Involve taking the documents (originally from CSV) and extract authors, organizations,
and recipients
Also involve converting organization names to their official, clean names
"""
import time
import json
from pathlib import Path
import unittest
from collections import Counter
import pandas as pd
from person import Person
from people_db import PeopleDatabase
from clean_org_names import get_clean_org_names

RAW_ORG_TO_CLEAN_ORG_DICT = get_clean_org_names()


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

    initial_time = time.time()

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
    print("Merging names took", time.time() - initial_time)

#    with open('alias_to_name.json', 'w') as outfile:
#        json.dump(people_db.get_alias_to_name(), outfile)


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
                orgs.add(RAW_ORG_TO_CLEAN_ORG_DICT[org])

            if len(orgs) != 1:
                continue
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


def load_documents_to_dataframe(path) -> pd.DataFrame:
    """
    Loads the Dunn documents into a pandas Dataframe
    :return: pd.DataFrame
    """
    df = pd.read_csv(path).fillna('')  # pylint: disable=C0103
    return df


def get_au_and_rc_by_document(path) -> list:
    """
    Creates a list of documents such that each element consists of a dict with keys
    'au', 'au_org', 'au_person' OR 'rc', 'rc_org', 'rc_person'.
    These keys map to info about the authors/recipients and organizations associated with docs
    :return: list
    """
    df = load_documents_to_dataframe(path)  # pylint: disable=C0103
    authors_by_docs = []
    for _, row in df.iterrows():
        authors_by_docs.append({
            'au': parse_column_person(row['au']),
            'au_org': parse_column_org(row['au_org']),
            'au_person': parse_column_person(row['au_person'])
        })
    recipients_by_docs = []
    for _, row in df.iterrows():
        recipients_by_docs.append({
            'rc': parse_column_person(row['rc']),
            'rc_org': parse_column_org(row['rc_org']),
            'rc_person': parse_column_person(row['rc_person'])
        })
    return [authors_by_docs, recipients_by_docs]


def parse_column_person(column_name):
    """
    Splits individual names by semicolon or bar (|)

    :param column_name: list, taken from csv with doc info
    :return: list, names of people in column
    """
    names = []
    for name_split_semicolon in [n.strip() for n in column_name.split(';')]:
        for name_split_bar in [m.strip() for m in name_split_semicolon.split('|')]:
            if 0 < len(name_split_bar) < 100:
                names.append(name_split_bar)
    return names


def parse_column_org(column_org):
    """
    Splits individual organizations by semicolon, bar (|) or comma

    :param column_org: list, column of organization names taken from csv with doc info
    :return: list of organization names
    """
    organizations = []
    for name_split_semicolon in [n.strip() for n in column_org.split(';')]:
        for name_split_bar in [m.strip() for m in name_split_semicolon.split('|')]:
            for name_split_comma in [m.strip() for m in name_split_bar.split(',')]:
                if 0 < len(name_split_comma) < 100:
                    organizations.append(name_split_comma)

    return organizations


class TestAddPositions(unittest.TestCase):
    """Tests adding positions to people in a people database
    Attributes:
        people_db: an expected people database
    """
    def setUp(self):
        self.people_db = PeopleDatabase()
        for name in ['Dunn, WL', 'Garcia, Raquel', 'Risi, Stephan']:
            self.people_db.add_person_raw(name, 1)

    def test_add_au_and_rc_org(self):
        """
        Test add_au_and_rc_function
        """
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


if __name__ == '__main__':
    unittest.main()
