import time
import json
from pathlib import Path
import pickle
import unittest
from collections import Counter
import pandas as pd
from person import Person
from people_db import PeopleDatabase
from clean_org_names import RAW_ORG_TO_CLEAN_ORG_DICT
from IPython import embed

from .name_preprocessing import parse_column_person


def load_1970s_network():

    network_path = Path('..', 'data', 'network_generation', 'network_1970s.pickle')

    try:
        with open(network_path) as infile:
            network = pickle.load(infile)
            return network
    except FileNotFoundError:

        print("Precomputed network for the 1970s does not exist. Generating now...")

        docs_csv_path = Path('..', 'data', 'documents', 'docs_1970s_all.csv')
        people_db_path = Path('..', 'data', 'name_disambiguation', 'people_db_1970s.pickle')

        people_db = PeopleDatabase()
        people_db.load_from_disk(Path(people_db_path))

        df = pd.read_csv(docs_csv_path).fillna('')  # pylint: disable=C0103

        nodes = {}
        edges = {}
        for idx, doc in df.iterrows():  # iterate over all documentsf
            if idx % 1000 == 0:
                print(idx)

            doc_authors = []
            doc_recipients = []
            for person in parse_column_person(doc['au']) + parse_column_person(doc['au_person']):
                try:
                    doc_authors.append(people_db.alias_to_person_dict[person])
                except KeyError:
                    print(f"missing: {person}")
            for person in parse_column_person(doc['rc']) + parse_column_person(doc['rc_person']):
                try:
                    doc_recipients.append(people_db.alias_to_person_dict[person])
                except KeyError:
                    print(f'Missing: {person}')

            for author in doc_authors:
                if author in nodes:
                    nodes[author]['count_authored'] += 1
                else:
                    nodes[author] = {'person': author, 'count_authored': 1, 'count_received': 0}

            for recipient in doc_recipients:
                if recipient in nodes:
                    nodes[recipient]['count_received'] += 1
                else:
                    nodes[recipient] = {'person': recipient, 'count_authored': 0,
                                        'count_received': 1}

            for author in doc_authors:
                for recipient in doc_recipients:
                    edge = tuple(sorted([author, recipient]))
                    if edge in edges:
                        edges[edge]['count'] += 1
                    else:
                        edges[edge] = {'edge': edge, 'count': 1}

        with open(network_path, 'wb') as out:
            network = {'nodes': nodes, 'edges': edges}
            pickle.dump(network, out)

        return network


def generate_network_of_top_n_edges(n_edges=300):
    pass

if __name__ == '__main__':
    load_1970s_network()
