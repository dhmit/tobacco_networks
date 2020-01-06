"""
This file contains the code to generate networks that can then be rendered through react/D3
"""

import json
import pickle
from collections import Counter
from pathlib import Path

from IPython import embed

import pandas as pd

from name_disambiguation.name_preprocessing import parse_column_person, parse_column_org
from name_disambiguation.people_db import PeopleDatabase
from name_disambiguation.config import COMPANY_ABBREVIATIONS_TO_SKIP
from name_disambiguation.person import Person

from name_disambiguation.clean_org_names import RAW_ORG_TO_CLEAN_ORG_DICT


NAMES_TO_SKIP = {
    "*. Tobacco Company",
    "A. J. Ahrensfeld-tf",
    "American Brands Inc",
    "Arnold &. Porter",
        "Cim Evaluation Team",
    "Council For tobacco Research",
        "Hardy & bacon Shook",
    "Ici America",
    "I. Hcr",
    "Nabisco",
    "Quality Control Div",
    "Marketing Research Dept",
    "Shook Hardy",
    "Simon Fraser univ Sterling",
    "Testing Laboratory Steele-wl",
    "Tobacco Assoc",
    "U. S. Tobacco",
}


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

        print("Willix", people_db.get_person_from_alias('Willix-J, SSC&B'))

        nodes = {}
        edges = {}
        missing_nodes = Counter()
        for idx, doc in df.iterrows():  # iterate over all documentsf
            if idx % 1000 == 0:
                print(idx)

            doc_authors = []
            doc_recipients = []
            for person in parse_column_person(doc['au']) + parse_column_person(doc['au_person']):

                db_person = people_db.get_person_from_alias(person)
                if db_person:
                    doc_authors.append(db_person)
                else:
                    if not (
                        person.lower().replace(' ', '') in COMPANY_ABBREVIATIONS_TO_SKIP or
                        person in RAW_ORG_TO_CLEAN_ORG_DICT
                    ):
                        print(f"\n\nMissing: {person}")
                        missing_nodes[person] += 1
                        p = Person(person)
                        print(p)
                        embed()

            for person in parse_column_person(doc['rc']) + parse_column_person(doc['rc_person']):
                db_person = people_db.get_person_from_alias(person)
                if db_person:
                    doc_recipients.append(db_person)
                else:
                    if not person.lower().replace(' ', '') in COMPANY_ABBREVIATIONS_TO_SKIP:
                        print(f'Missing: {person}')
                        missing_nodes[person] += 1

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

def store_network_for_visualization(nodes, edges, center_names, network_name, file_name):
    """
    Stores the data for one backend in backend/data
    :param nodes: dict
    :param edges: dict
    :param center_names: list   The names at the center of the network that should be highlighted.
    :param network_name: str
    :param file_name: str
    :return:
    """

    network = {
        'name': network_name,
        'nodes': nodes,
        'links': edges,
        'center_names': {name:True for name in center_names}    # dict bc set can't be jsoned.
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

def generate_people_network(names, network_name, max_number_of_nodes=100,   # pylint: disable=R0914
                            include_2nd_degree_connections=False):

    """
    Generate the network of one or multiple people. The resulting json is stored in
    backend/data
    :param names: list
    :param network_name: str
    :param max_number_of_nodes: int
    :return:
    """
    if include_2nd_degree_connections:
        network_name += '_including_2nd_degree_edges'

    # Load people db
    people_db_path = Path('..', 'data', 'network_generation', '1970s_from_csv.pickle')
    people_db = PeopleDatabase()
    people_db.load_from_disk(Path(people_db_path))

    # initialize the center group of people
    center_people = set()
    for name in names:
        db_person = people_db.get_person_from_alias(name)
        if db_person:
            center_people.add(db_person)
        else:
            print(f'Could not find {name}. Possible candidates: ')
            possible_matches = search_possible_matches(name[:5], people_db)
            for result in possible_matches.most_common(5):
                print(result)
            raise KeyError

    # load the whole 1970s network
    network = load_1970s_network()
    edges = network['edges']

    nodes_temp = Counter()
    edges_out = []
    nodes_out = []

    c = Counter()

    # first identify all the primary edges including at least one person from center_people
    for idx, edge in enumerate(edges.values()):

        person1 = people_db.get_person_from_alias(edge['edge'][0].aliases.most_common(1)[0][0])
        person2 = people_db.get_person_from_alias(edge['edge'][1].aliases.most_common(1)[0][0])

        if not person1 or not person2:
            embed()
        # person1, person2 = edge['edge']
        #
        # if edge['edge'][0].last.lower().find('holtzman') > -1:
        #     print(person1)
        #     print(edge['edge'][0])
        #     print("roemer")
        #     # embed()

        if (
            (person1 in center_people or person2 in center_people) and
            (person1.first != '' or person1.most_likely_position != 'no positions available') and
            (person2.first != '' or person2.most_likely_position != 'no positions available') and
            (person1.full_name not in NAMES_TO_SKIP) and
            (person2.full_name not in NAMES_TO_SKIP)
        ):
            edges_out.append({'node1': person1.full_name, 'node2': person2.full_name,
                              'docs': edge['count'], 'words': 0})
            nodes_temp[person1] += edge['count']
            nodes_temp[person2] += edge['count']

            if person1 in center_people:
                c[person1] += 1
            if person2 in center_people:
                c[person2] += 1


    print("showing number of documents per central person")
    for p, count in c.most_common():
        print(count, p.full_name)
    if len(c) != len(center_people):
        raise ValueError("Found 0 documents for at least one person. embed here and investigate!")



    # embed()

    # # select edges to include:
    # for edge in sorted(edges_out, key=lambda x: x['docs'], reverse=True):
    #
    #     if len(nodes_temp) >= max_number_of_nodes:
    #         break
    #
    #     p1 = people_db.get_person_from_alias(edge['node1'])
    #     p2 = people_db.get_person_from_alias(edge['node2'])
    #     if (
    #             (p1.first == '' and p1.most_likely_position == 'no positions available') or
    #             (p2.first == '' and p2.most_likely_position == 'no positions available')
    #         ):
    #         continue
    #
    #     edges_out.append(edge)
    #     nodes_temp[p1] += edge['docs']
    #     nodes_temp[p1] += edge['docs']

    # embed()

    new_people_db = PeopleDatabase()
    for node, node_count in nodes_temp.most_common(200):
        print("\n", node_count, "\n", node)
        node.count = node_count
        new_people_db.people.add(node)
    new_people_db.generate_alias_to_person_dict()
    new_people_db.merge_duplicates(manual_merge=True)


    for node in sorted(new_people_db.people, key = lambda x: x.count)[::-1]:
        nodes_out.append({'name': node.full_name, 'docs': nodes_temp[node], 'words': 0,
                          'affiliation': node.most_likely_position})

    edges_out = []
    for edge in edges.values():
        # with additional merges, the people in the db have changed -> we need to look them
        # up again via one of their aliases.
        p1 = new_people_db.get_person_from_alias(edge['edge'][0].aliases.most_common(1)[0][0])
        p2 = new_people_db.get_person_from_alias(edge['edge'][1].aliases.most_common(1)[0][0])
        if p1 and p2:
            if(
                p1.full_name in center_people or
                p2.full_name in center_people or
                (
                    include_2nd_degree_connections and
                    edge['count'] > 5
                )
            ):
                edges_out.append({'node1': p1.full_name, 'node2': p2.full_name,
                                'docs': edge['count'], 'words': 0})
                if edge['count'] == 0:
                    embed()

    # embed()

    # if include_2nd_degree_connections:
        # network_name += '_including_2nd_degree_edges'

    #
    # # add connections between non-main nodes
    # # we now know all the nodes, we just need to re-generate edges
    # # TODO: this is highly inefficient--we should first figure out all of the nodes and only then
    # # TODO: generate edges. but it works for the time being.
    # if include_2nd_degree_connections:
    #
    #     network_name += '_including_2nd_degree_edges'
    #
    #     node_names_set = set(node['name'] for node in nodes_out)
    #     edges_final = []
    #     for idx, edge in enumerate(edges.values()):
    #         if edge['count'] < 5:
    #             continue
    #
    #         person1, person2 = edge['edge']
    #         if (person1.full_name in node_names_set and
    #                 person2.full_name in node_names_set):
    #             edges_final.append({'node1': person1.full_name, 'node2': person2.full_name,
    #                                 'docs': edge['count'], 'words': 0})
    #     edges_final = sorted(edges_final, key=lambda x: x['docs'], reverse=True)
    # else:
    #     edges_final = edges_out

    store_network_for_visualization(nodes_out, edges_out,
                                    center_names=names,
                                    network_name=f'person_{network_name}',
                                    file_name=f'person_{network_name}.json')

    # embed()

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
    for person in people_db._alias_to_person_dict:
        if person.lower().find(name.lower()) > -1:
            person_obj = people_db._alias_to_person_dict[person]
            possible_matches[person_obj] = person_obj.count

    return possible_matches


def generate_network_thedore_sterling():        # pylint: disable=C0103
    """
    Generate the network of Theodore Sterling, the largest recipient of CTR Special Project Grants
    For more on Stering, see http://tobacco-analytics.org/case/ctr
    """
    generate_people_network(names=['STERLING,TD'], network_name='sterling',
                            max_number_of_nodes=100)


def generate_network_lawyers(include_2nd_degree_connections=True):
    """
    Generates the network for the industry's general counsels, ca. 1972
    For more on them and in particular the CTR, see http://tobacco-analytics.org/case/ctr

    :param: include_second_degree_connections: if true, include edges between nodes that are
                                                in the network but not main nades.

    :return:
    """

    names = ['Thomas F. Ahrensfeld',    # y     Philip Morris
             'Alexander Holtzman',      # y     Philip Morris
             'H. Debaun Bryant',        # y     Brown & Williamson
             'Frederick P. Haas',       # y     Liggett & Myers
             'Cyril F. Hetsko',         # y     American Tobacco
             'Henry C. Roemer',         # y     R.J. Reynolds
             'Arthur Joseph Stevens',   # y     Lorillard
             'Addison Y. Yeaman',       # y     Brown & Williamson ??possibly also CTR??
             'William W. Shinn',        # y     Shook, Hardy & Bacon (CTR law firm)
             'David Ross Hardy'         # y     Shook, Hardy & Bacon (CTR law firm)
             ]

    generate_people_network(names=names, network_name='lawyers',
                            max_number_of_nodes=200,
                            include_2nd_degree_connections=include_2nd_degree_connections)

def generate_network_research_directors(include_2nd_degree_connections=True):# pylint: disable=C0103
    """
    Generates the network of industry research directors, ca. 1970
    """

    names = [
        'Ivor Wallace Hughes',          # Brown & Williamson
        'Preston Hildebrand Leake',     # American Tobacco
        'Murray Senkus',                # R. J. Reynolds
        'Alexander White Spears',       # Lorillard
        'Helmut R. Wakeham',            # Philip Morris
        'Henry H. Ramm',                # Council for Tobacco Research
        'Robert Casad Hockett'          # Council for Tobacco Research
    ]

    generate_people_network(names=names, network_name='research_directors',
                            max_number_of_nodes=300,
                            include_2nd_degree_connections=include_2nd_degree_connections)


def generate_network_whole_industry():
    """
    Generate a network where the nodes are not people but companies

    :return:
    """

    # Load people db
    people_db_path = Path('..', 'data', 'network_generation', 'people_db_1970s.pickle')
    people_db = PeopleDatabase()
    people_db.load_from_disk(Path(people_db_path))

    # load the whole 1970s network
    network = load_1970s_network()
    edges = network['edges']

    org_counter = Counter()
    connection_counter = Counter()


    # first identify all the primary edges including at least one person from center_people
    for idx, edge in enumerate(edges.values()):
        person1, person2 = edge['edge']
        p1m = person1.most_likely_position
        p2m = person2.most_likely_position
        if (
            person1 and person2 and p1m != p2m and
            p1m != 'no positions available' and p2m != 'no positions available'
        ):
            org_counter[p1m] += edge['count']
            org_counter[p2m] += edge['count']
            connection_counter[tuple(sorted((p1m, p2m)))] += edge['count']

    nodes = []
    edges = []
    for org, org_count in org_counter.most_common():
        nodes.append({'name': org, 'docs': org_count, 'words': 0, 'affiliation': 'test'})
    for edge, edge_count in connection_counter.most_common():
        edges.append({'node1': edge[0], 'node2': edge[1], 'docs': edge_count, 'words': 0})

    store_network_for_visualization(nodes, edges,
                                    center_names=[], network_name='industry',
                                    file_name='whole_industry.json')

if __name__ == '__main__':

    # for match in search_possible_matches('leake').most_common(10):
    #     print()
    #     print(match[0].full_name, match[1])
    #     print(match[0].positions)
    #     print(match[0].aliases)

    # generate_network_research_directors(include_2nd_degree_connections=True)
    generate_network_lawyers(include_2nd_degree_connections=True)
    # generate_network_whole_industry()
