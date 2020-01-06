"""
Contains helper functions:
Create and pickles a People Database from CSV
Extract author and recipient aliases from CSV with documents info
Involve taking the documents (originally from CSV) and extract authors, organizations,
and recipients
Also involve converting organization names to their official, clean names
"""
import json
import time
import unittest

import pandas as pd

from name_disambiguation.people_db import PeopleDatabase


def merge_names_from_json_file(json_name_file, people_db_pickle_file):
    """
    Creates a people db from reading json file (dict of raw names and counts) and merges people
    in it. Stores people db in a pickle file
    :param json_name_file: Path to json file
    :param people_db_pickle_file: Path for output pickle file of the created PeopleDB
    :return:
    """

    with open(json_name_file, 'r') as infile:
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

    people_db.store_to_disk(people_db_pickle_file)
    print("Merging names took", time.time() - initial_time)


def get_au_and_rc_by_document(path, return_type='both') -> list:
    """
    Creates a list of documents such that each element consists of a dict with keys

    returns either just information about the authors, the recipients, or both

    Note(SR): to give authors and recipients the same structure, I have renamed 'au' and 'rc'
    to general.

    'au', 'au_org', 'au_person' OR 'rc', 'rc_org', 'rc_person'.
    These keys map to info about the authors/recipients and organizations associated with docs
    :param path: Path
    :param return_type: str
    :return: list
    """

    if return_type not in ['authors', 'recipients', 'both']:
        raise ValueError(f'get_au_and_rc_by_document can only be called with return_type "both",'
                         f'"authors," or "recipients".')

    df = pd.read_csv(path).fillna('')  # pylint: disable=C0103

    authors_by_docs = []
    recipients_by_docs = []
    for _, row in df.iterrows():
        authors_by_docs.append({
            'general': parse_column_person(row['au']),
            'organization': parse_column_org(row['au_org']),
            'person': parse_column_person(row['au_person'])
        })
        recipients_by_docs.append({
            'general': parse_column_person(row['rc']),
            'organization': parse_column_org(row['rc_org']),
            'person': parse_column_person(row['rc_person'])
        })

    if return_type == 'authors':
        return authors_by_docs
    elif return_type == 'recipients':
        return recipients_by_docs
    # if we return both, we just add recipients to the authors list
    else:
        return authors_by_docs + recipients_by_docs


def parse_column_person(column_name):
    """
    Splits individual names by semicolon or bar (|)

    :param column_name: list, taken from csv with doc info
    :return: list, names of people in column
    """
    names = []
    for name_split_semicolon in [n.strip() for n in column_name.split(';')]:
        for name_split_bar in [m.strip() for m in name_split_semicolon.split('|')]:
            if 0 < len(name_split_bar) < 100:   # pylint: disable=C1801
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
                if 0 < len(name_split_comma) < 100:     # pylint: disable=C1801
                    organizations.append(name_split_comma)

    return organizations


if __name__ == '__main__':

    unittest.main()
