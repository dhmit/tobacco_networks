"""
This file contains the code to generate networks that can then be rendered through react/D3
"""

import json
import pickle
from collections import Counter
from pathlib import Path

import pandas as pd

from name_disambiguation.name_preprocessing import parse_column_person
from people_db import PeopleDatabase


def load_1970s_network():       # pylint: disable=R0914
    """
    Loads (or, if necessary, generates, the entire network for the 1970s, which is the basis
    for generating sub-networks

    :return:
    """

    network_path = Path('..', 'data', 'network_generation', 'network_1970s.pickle')

    try:
        with open(network_path, 'rb') as infile:
            return pickle.load(infile)
    except FileNotFoundError:

        print("Precomputed network for the 1970s does not exist. Generating now...")

        docs_csv_path = Path('..', 'data', 'documents', 'docs_1970s_all.csv')
        people_db_path = Path('..', 'data', 'network_generation', 'people_db_1970s.pickle')

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

def store_network_for_visualization(nodes, edges, network_name, file_name):
    """
    Stores the data for one backend in backend/data

    :param nodes: dict
    :param edges: dict
    :param network_name: str
    :param file_name: str
    :return:
    """

    network = {
        'name': network_name,
        'nodes': nodes,
        'links': edges,
    }
    out_path = Path('..', 'backend', 'data', file_name)
    with open(out_path, 'w') as out:
        json.dump(network, out, sort_keys=True, indent=4)


def generate_network_of_top_n_edges(n_edges=100):
    """
    Generate the network consisting of the n strongest edges

    :param n_edges:
    :return:
    """

    network = load_1970s_network()
    edges = network['edges']

    nodes_temp = Counter()
    edges_out = []
    nodes_out = []

    for edge in sorted(edges.values(), key=lambda x: x['count'], reverse=True)[:n_edges]:
        edges_out.append({'node1': edge['edge'][0].full_name, 'node2': edge['edge'][1].full_name,
                          'docs': edge['count'], 'words': 0})

        nodes_temp[edge['edge'][0]] += edge['count']
        nodes_temp[edge['edge'][1]] += edge['count']

    for node in nodes_temp:
        nodes_out.append({'name': node.full_name, 'docs': nodes_temp[node], 'words': 0,
                          'affiliation': node.most_likely_position})

    store_network_for_visualization(nodes_out, edges_out, f'top_{n_edges}_edges',
                                    f'top_{n_edges}_edges.json')

def generate_people_network(names, network_name, max_number_of_nodes=100):  # pylint: disable=R0914

    """
    Generate the network of one or multiple people. The resulting json is stored in
    backend/data

    :param names: list
    :param network_name: str
    :param max_number_of_nodes: int
    :return:
    """

    people_db_path = Path('..', 'data', 'network_generation', 'people_db_1970s.pickle')
    people_db = PeopleDatabase()
    people_db.load_from_disk(Path(people_db_path))
    for person in people_db.people:
        people_db.alias_to_person_dict[person.full_name] = person

    center_people = []
    for name in names:
        try:
            center_people.append(people_db.alias_to_person_dict[name])
        except KeyError:
            print(f'Could not find {name}. Possible candidates: ')
            possible_matches = search_possible_matches(name[:5], people_db)
            for result in possible_matches.most_common(5):
                print(result)
            raise KeyError

    network = load_1970s_network()
    edges = network['edges']

    nodes_temp = Counter()
    edges_out = []
    nodes_out = []

    for idx, edge in enumerate(edges.values()):
        if idx % 1000 == 0:
            print(idx, len(edges))
        person1, person2 = edge['edge']
        if (person1 in center_people or person2 in center_people) and edge['count'] > 1:
            edges_out.append({'node1': person1.full_name, 'node2': person2.full_name,
                              'docs': edge['count'], 'words': 0})

    edges_out = sorted(edges_out, key=lambda x: x['docs'], reverse=True)[:max_number_of_nodes]
    for edge in edges_out:
        person1 = people_db.alias_to_person_dict[edge['node1']]
        person2 = people_db.alias_to_person_dict[edge['node2']]
        nodes_temp[person1] += edge['docs']
        nodes_temp[person2] += edge['docs']

    for node in nodes_temp:
        nodes_out.append({'name': node.full_name, 'docs': nodes_temp[node], 'words': 0,
                          'affiliation': node.most_likely_position})
        print(node.full_name, node.most_likely_position)

    print(len(nodes_out))

    store_network_for_visualization(nodes_out, edges_out, f'person_{network_name}',
                                    f'person_{network_name}.json')

def search_possible_matches(name, people_db=None):
    """
    Search for possible alias matches given a name

    :param name:
    :param people_db:
    :return: Counter
    """

    if not people_db:
        people_db_path = Path('..', 'data', 'network_generation', 'people_db_1970s.pickle')
        people_db = PeopleDatabase()
        people_db.load_from_disk(Path(people_db_path))

    possible_matches = Counter()
    for person in people_db.alias_to_person_dict:
        if person.lower().find(name.lower()) > -1:
            person_obj = people_db.alias_to_person_dict[person]
            possible_matches[person_obj] = person_obj.count

    return possible_matches


def generate_network_thedore_sterling():        # pylint: disable=C0103
    """
    Generate the network of Theodore Sterling, the largest recipient of CTR Special Project Grants
    For more on Stering, see http://tobacco-analytics.org/case/ctr

    """
    generate_people_network(names=['STERLING,TD'], network_name='sterling',
                            max_number_of_nodes=100)


def generate_network_lawyers():
    """
    Generates the network for the industry's general counsels, ca. 1972
    For more on them and in particular the CTR, see http://tobacco-analytics.org/case/ctr

    :return:
    """

    names = ['Ahrensfeld, Thomas F',    # Philip Morris
             'Holtzman, A',             # Philip Morris (Alexander)
             'BRYANT,D',                # Brown & Williamson
             'Haas, Frederick P.',      # Liggett & Myers
             'Hetsko, Cyril F.',        # American Tobacco
             'Roemer, Henry C. (Jack)', # R.J. Reynolds
             'Stevens, Arthur J',       # Lorillard
             'Yeaman, A',               # Brown & Williamson ??possibly also CTR??

             'Shinn, William W',        # Shook, Hardy & Bacon (CTR law firm)
             'Hardy, David Ross'        # Shook, Hardy & Bacon (CTR law firm)
             ]

    generate_people_network(names=names, network_name='lawyers',
                            max_number_of_nodes=300)

def generate_network_research_directors():      # pylint: disable=C0103
    """
    Generates the network of industry research directors, ca. 1970

    """

    names = [
        'Hughes, Ivor Wallace, Dr.',    # Brown & Williamson
        'Senkus, M.',                   # R.J. Reynolds
        'Spears, Alexander White, III', # Lorillard
        'Wakeham, H',                   # Philip Morris

        'Ramm, Henry H.',               # Council for Tobacco Research
        'Hockett, Robert Casad, Ph.D.'  # Council for Tobacco Research
    ]

    generate_people_network(names=names, network_name='research_directors',
                            max_number_of_nodes=300)


if __name__ == '__main__':
    generate_network_research_directors()
