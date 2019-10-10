from collections import Counter
from pathlib import Path
import json

import pandas as pd



def load_documents_to_dataframe() -> pd.DataFrame:
    """
    Loads the Dunn documents into a pandas Dataframe
    :return: pd.DataFrame
    """
    df = pd.read_csv(Path('..', 'data', 'name_disambiguation', 'dunn_docs.csv')).fillna('')
    return df


def get_author_counter() -> Counter:
    """
    Returns a counter of all authors in the Dunn documents

    >>> author_counter = get_author_counter()
    >>> author_counter.most_common(1)
    [('DUNN,WL', 2566)]

    :return: Counter
    """

    df = load_documents_to_dataframe()
    name_counter = Counter()
    for _, row in df.iterrows():
        for category in ['au', 'au_person']:  # don't use author organization to get authors
            name = row[category]
            if name:
                for name_split_semicolon in [n.strip() for n in name.split(';')]:
                    for name_split_bar in [m.strip() for m in name_split_semicolon.split('|')]:
                        if len(name_split_bar) > 0:
                            name_counter[name_split_bar] += 1
                            if len(name_split_bar) > 100:
                                print('unusually long name', name_split_bar)

    return name_counter


def get_authors_by_document() -> list:
    """
    Creates a list of documents such that each element consists of a dict with keys
    'au', 'au_org', 'au_person'

    >>> authors_by_docs = get_authors_by_document()
    >>> authors_by_docs[0]
    {'au': '', 'au_org': '', 'au_person': 'BOWLING,JC'}

    :return: list
    """

    df = load_documents_to_dataframe()
    authors_by_docs = []
    for _, row in df.iterrows():
        authors_by_docs.append({
            'au': parse_au_person(row['au']),
            'au_org': parse_au_org(row['au_org']),
            'au_person': parse_au_person(row['au_person'])
        })
    return authors_by_docs

def parse_au_person(au_person):
    names = []
    for name_split_semicolon in [n.strip() for n in au_person.split(';')]:
        for name_split_bar in [m.strip() for m in name_split_semicolon.split('|')]:
            if 0 < len(name_split_bar) < 100:
                names.append(name_split_bar)
    return names

def parse_au_org(au_org):
    names = []
    for name_split_semicolon in [n.strip() for n in au_org.split(';')]:
        for name_split_bar in [m.strip() for m in name_split_semicolon.split('|')]:
            for name_split_comma in [m.strip() for m in name_split_bar.split(',')]:
                if 0 < len(name_split_comma) < 100:
                    names.append(name_split_comma)
    return names

def get_clean_org_names():
    # read clean_org_names
    file_name = Path('..', 'data', 'name_disambiguation', 'clean_org_names_to_raw_org_names.json')
    with open(file_name, 'r') as infile:
        name_dict = json.load(infile)

    # invert dict
    inv_name_dict = {}
    for official in name_dict:
        for j in name_dict[official]:
            inv_name_dict[j] = official
    return inv_name_dict


if __name__ == '__main__':
    get_author_counter()
