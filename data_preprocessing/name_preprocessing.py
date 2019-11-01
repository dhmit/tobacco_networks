from collections import Counter
from pathlib import Path
import json

import pandas as pd


def load_documents_to_dataframe(path) -> pd.DataFrame:
    """
    Loads the Dunn documents into a pandas Dataframe
    :return: pd.DataFrame
    """
    df = pd.read_csv(path).fillna('')
    return df


def get_au_and_rc_by_document(path) -> list:
    """
    Creates a list of documents such that each element consists of a dict with keys
    'au', 'au_org', 'au_person' OR 'rc', 'rc_org', 'rc_person'.
    These keys map to info about the authors/recipients and organizations associated with docs

    >>> authors_by_docs = get_au_and_rc_by_document()
    >>> authors_by_docs[0]
    {'au': '', 'au_org': '', 'au_person': 'BOWLING,JC'}
    :return: list
    """
    dframe = load_documents_to_dataframe(path)
    authors_by_docs = []
    for _, row in dframe.iterrows():
        authors_by_docs.append({
            'au': parse_column_person(row['au']),
            'au_org': parse_column_org(row['au_org']),
            'au_person': parse_column_person(row['au_person'])
        })
    recipients_by_docs = []
    for _, row in dframe.iterrows():
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
    TODO: Do we really need to split by comma?

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


def get_clean_org_names():
    """
    :return: dict, maps official organization names to all their variants
    """
    # read clean_org_names
    file_name = Path('..', 'data', 'name_disambiguation', 'clean_org_names_to_raw_org_names.json')
    with open(file_name, 'r') as infile:
        name_dict = json.load(infile)

    # invert dict
    inv_name_dict = {}
    for official in name_dict:
        for j in name_dict[official]:
            inv_name_dict[j] = official
        inv_name_dict[official] = official
    return inv_name_dict


if __name__ == '__main__':
    pass
