"""
This file contains the code to generate networks that can then be rendered through react/D3

TODO: this should really be done through a network class where each network has nodes, edges, and
TODO: documents and the ability to output the resulting network to json
"""

import json
import pickle
import re
from collections import Counter
from pathlib import Path
import random

import pandas as pd
from IPython import embed

from name_disambiguation.name_preprocessing import parse_column_person
from name_disambiguation.people_db import PeopleDatabase
from name_disambiguation.person import Person

DOCS_CSV_PATH = Path('..', 'data', 'documents', 'docs_1970s_all.csv')
NETWORK_PATH = Path('..', 'data', 'network_generation', 'network_1970s.pickle')
PEOPLE_DB_PATH = Path('..', 'data', 'network_generation', '1970s_from_csv.pickle')
NAMES_TO_SKIP = {
    'American Brands Inc',
    'Hardy Shook',
    'Shook Hardy',
}

def create_db_of_1970s_docs_from_csv():             # pylint: disable=C0103
    """
    We have this strange 1970s db from November 2019 but I don't know how it was created.
    This script simply uses the docs_1970s_all.csv to create a people_db using the info found in
    those documents.

    :return:
    """

    print("Generating new 1970s People DB")

    df = pd.read_csv(DOCS_CSV_PATH).fillna('')      # pylint: disable=C0103
    people_db = PeopleDatabase()

    counters = {
        'valid': Counter(),         # valid person
        'organization_from_person': Counter(),  # valid organizations extracted from person col
        'organization_from_org': Counter(),  # valid organizations extracted from org col
        'organization_invalid': Counter(), # invalid organizations from org col
        'invalid': Counter(),       # not a valid person
        'error': Counter(),         # threw an error
    }

    for idx, doc in df.iterrows():  # iterate over all documentsf
        if idx % 1000 == 0:
            print(idx)

        doc_authors, doc_author_orgs = parse_authors_or_recipients_of_doc('authors', doc,
                                                                          counters, people_db)
        doc_recipients, doc_recipient_orgs = parse_authors_or_recipients_of_doc('recipients', doc,
                                                                                counters, people_db)

        doc_author_orgs += parse_au_or_rc_organizations_of_doc('authors', doc, counters, people_db)
        doc_recipient_orgs += parse_au_or_rc_organizations_of_doc('recipients', doc, counters,
                                                                  people_db)

        for person in doc_authors:
            people_db.add_person_raw(name_raw=person, position=Counter(doc_author_orgs))
        for person in doc_recipients:
            people_db.add_person_raw(name_raw=person, position=Counter(doc_recipient_orgs))

    len_before_merge = len(people_db)
    people_db.merge_duplicates()
    print("before", len_before_merge, ". after", len(people_db))

    people_db.store_to_disk(PEOPLE_DB_PATH)


def get_network_of_1970s_nodes_and_edges():             # pylint: disable=C0103,R0914
    """
    Get or create a network of nodes and edges based on the 1970s people database

    :return:
    """

    try:
        with open(NETWORK_PATH, 'rb') as infile:
            return pickle.load(infile)
    except FileNotFoundError:

        print("no 1970s network found. generating now...")
        people_db = PeopleDatabase()
        try:
            people_db.load_from_disk(PEOPLE_DB_PATH)
        except FileNotFoundError:
            create_db_of_1970s_docs_from_csv()
            people_db.load_from_disk(PEOPLE_DB_PATH)


        df = pd.read_csv(DOCS_CSV_PATH).fillna('')      # pylint: disable=C0103

        nodes = {}
        edges = {}
        counters = {
            'valid': Counter(),         # valid person
            'organization_from_person': Counter(),  # valid organizations extracted from person col
            'organization_from_org': Counter(),  # valid organizations extracted from org col
            'organization_invalid': Counter(), # invalid organizations from org col
            'invalid': Counter(),       # not a valid person
            'error': Counter(),         # threw an error
        }


        for idx, doc in df.iterrows():  # iterate over all documentsf
            if idx % 1000 == 0:
                print(idx)

            doc_authors, _ = parse_authors_or_recipients_of_doc('authors', doc, counters, people_db)
            doc_recipients, _ = parse_authors_or_recipients_of_doc('recipients', doc,
                                                                   counters, people_db)

            d_authors = []
            for author in doc_authors:
                author_person = people_db.get_person_from_alias(author)
                if author_person:
                    d_authors.append(author_person)
                else:
                    print("could not find", author)
            doc_authors = d_authors

            d_recipients = []
            for recipient in doc_recipients:
                recipient_person = people_db.get_person_from_alias(recipient)
                if recipient_person:
                    d_recipients.append(recipient_person)
                else:
                    print("Could not find", recipient)
            doc_recipients = d_recipients

            for author in doc_authors:
                author.docs_authored.add(doc.tid)
                if author in nodes:
                    nodes[author]['count_authored'] += 1
                else:
                    nodes[author] = {'person': author, 'count_authored': 0, 'count_received': 0}

            for recipient in doc_recipients:
                recipient.docs_received.add(doc.tid)
                if recipient in nodes:
                    nodes[recipient]['count_received'] += 1
                else:
                    nodes[recipient] = {'person': recipient, 'count_authored': 0,
                                        'count_received': 1}

            for author in doc_authors:
                for recipient in doc_recipients:
                    edge = tuple(sorted([author, recipient]))
                    if edge in edges:
                        edges[edge]['docs'].add(doc.tid)
                    else:
                        edges[edge] = {'edge': edge, 'docs': {doc.tid} }

        embed()

        with open(NETWORK_PATH, 'wb') as out:
            network = {'nodes': nodes, 'edges': edges}
            pickle.dump(network, out)

        return get_network_of_1970s_nodes_and_edges()

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
    people_db = PeopleDatabase()
    people_db.load_from_disk(Path(PEOPLE_DB_PATH))


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
    network = get_network_of_1970s_nodes_and_edges()
    edges = network['edges']

    nodes_temp = Counter()
    # edges_out = []
    nodes_out = []

    center_person_doc_counter = Counter()

    # first identify all the primary edges including at least one person from center_people
    for idx, edge in enumerate(edges.values()):

        person1 = people_db.get_person_from_alias(edge['edge'][0].aliases.most_common(1)[0][0])
        person2 = people_db.get_person_from_alias(edge['edge'][1].aliases.most_common(1)[0][0])

        embed()

        if not person1 or not person2:
            print("could not find person1 or 2. embedding...")
            embed()
        if (
                (person1 in center_people or person2 in center_people) and     # pylint: disable=R0916
                (person1.first != '' or person1.most_likely_position != 'no positions available')
                and
                (person2.first != '' or person2.most_likely_position != 'no positions available')
                and
                (person1.full_name not in NAMES_TO_SKIP) and
                (person2.full_name not in NAMES_TO_SKIP)
        ):
            nodes_temp[person1] += len(edge['docs'])
            nodes_temp[person2] += len(edge['docs'])

            if person1 in center_people:
                center_person_doc_counter[person1] += 1
            if person2 in center_people:
                center_person_doc_counter[person2] += 1


    print("showing number of documents per central person")
    for person, count in center_person_doc_counter.most_common():
        print(count, person.full_name)
    if len(center_person_doc_counter) != len(center_people):
        raise ValueError("Found 0 documents for at least one person. embed here and investigate!")

    # store all people in the network to be displayed in their own network
    new_people_db = PeopleDatabase()
    for node, node_count in nodes_temp.most_common(max_number_of_nodes):
        print("\n", node_count, "\n", node)
        node.count = node_count
        new_people_db.people.add(node)
    new_people_db.generate_alias_to_person_dict()
    new_people_db.merge_duplicates(manual_merge=True)

    documents_out = set()
    for node in sorted(new_people_db.people, key=lambda x: x.count)[::-1]:
        embed()
        nodes_out.append({'name': node.full_name, 'docs': nodes_temp[node],
                          'affiliation': node.most_likely_position,
                          'sample_docs_authored': 0})

    edges_out = []
    for edge in edges.values():
        # with additional merges, the people in the db have changed -> we need to look them
        # up again via one of their aliases.
        person1 = new_people_db.get_person_from_alias(edge['edge'][0].aliases.most_common(1)[0][0])
        person2 = new_people_db.get_person_from_alias(edge['edge'][1].aliases.most_common(1)[0][0])

        if person1 and person2:
            if(
                    person1 in center_people or
                    person2 in center_people or
                    (
                        include_2nd_degree_connections and
                        len(edge['docs']) > 5
                    )
            ):
                if len(edge['docs']) == 0:
                    raise ValueError("count of edge should not be zero.")

                for tid in edge['docs']:
                    documents_out.add(tid)
                edges_out.append({'node1': person1.full_name, 'node2': person2.full_name,
                                  'docs': len(edge['docs'])})

    embed()

    store_network_for_visualization(nodes_out, edges_out,
                                    center_names=names,
                                    network_name=f'person_{network_name}',
                                    file_name=f'person_{network_name}.json')


def search_possible_matches(name, people_db=None):
    """
    Search for possible alias matches given a name
    :param name:
    :param people_db:
    :return: Counter
    """

    if not people_db:
        people_db = PeopleDatabase()
        people_db.load_from_disk(Path(PEOPLE_DB_PATH))

    possible_matches = Counter()

    for person in people_db._alias_to_person_dict:          # pylint: disable=W0212
        person_db = people_db.get_person_from_alias(name)
        if person_db:
            person_obj = people_db.get[person]
            possible_matches[person_obj] = person_obj.count

    return possible_matches


def parse_authors_or_recipients_of_doc(side, doc, counters, people_db):     # pylint: disable=C0103
    """

    Parse one csv row and get persons back

    :param side:
    :param doc:
    :param counters:
    :param people_db:
    :return:
    """

    if not side in ['authors', 'recipients']:
        raise ValueError("side has to be 'authors' or 'recipients' ")

    doc_organizations = []
    doc_people = []
    if side == 'authors':
        group = parse_column_person(doc['au']) + parse_column_person(doc['au_person'])
    else:
        group = parse_column_person(doc['rc']) + parse_column_person(doc['rc_person'])

    for name in group:
        try:
            if name in people_db.raw_org_to_clean_org_dict:
                doc_organizations.append(people_db.raw_org_to_clean_org_dict[name])
                continue
            # 4 characters is too short for a name and we have already extracted orgs
            if len(name) < 4:
                continue

            person = Person(name_raw=name)
            if person.check_if_this_person_looks_valid():
                doc_people.append(name)
                counters['valid'][name] += 1
            elif check_if_name_looks_like_an_organization(name):
                doc_organizations.append(name)
                counters['organization_from_person'][name] += 1
            else:
                counters['invalid'][name] += 1

        except:    # pylint: disable=W0702
            counters['error'][name] += 1

    return doc_people, doc_organizations

def parse_au_or_rc_organizations_of_doc(side, doc, counters, people_db):    # pylint: disable=C0103
    """
    Parse one csv and get organizations back

    :param side:
    :param doc:
    :param counters:
    :param people_db:
    :return:
    """

    if not side in ['authors', 'recipients']:
        raise ValueError("side has to be 'authors' or 'recipients' ")


    if side == 'authors':
        group = parse_column_person(doc['au_org'])
        # many person/org combinations only differ in terms of spaces. unclear why
        if (
                doc['au_org'].replace(' ', '') == doc['au'].replace(' ', '') or
                doc['au_org'].replace(' ', '') == doc['au_person'].replace(' ', '')
        ):
            return []
    else:
        group = parse_column_person(doc['rc_org'])
        if (
                doc['rc_org'].replace(' ', '') == doc['rc'].replace(' ', '') or
                doc['rc_org'].replace(' ', '') == doc['rc_person'].replace(' ', '')
        ):
            return []

    if len(group) == 0:
        return []


    organizations = []
    for org in group:
        if org in people_db.raw_org_to_clean_org_dict:
            organizations.append(people_db.raw_org_to_clean_org_dict[org])
        else:
            if check_if_name_looks_like_an_organization(org):
                organizations.append(org)
                counters['organization_from_org'][org] += 1
            else:
                counters['organization_invalid'][org] += 1

    return organizations


def check_if_name_looks_like_an_organization(name):     # pylint: disable=C0103
    """
    Returns true if the name looks like an organization
    currently: if only alphabetical and with at least 2 spaces

    >>> check_if_name_looks_like_an_organization('US HOUSE COMM ON INTERSTATE')
    True
    >>> check_if_name_looks_like_an_organization('US CONGRESS')
    False

    :param name:
    :return:
    """
    if re.match('^[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z ]+$', name):
        return True
    return False

# TODO: get the top_n_edges function to work again after updating the other functions in this file.
# def generate_network_of_top_n_edges(n_edges=100):
#     """
#     Generate the network consisting of the n strongest edges
#     :param n_edges:
#     :return:
#     """
#
#     network = get_network_of_1970s_nodes_and_edges()
#     edges = network['edges']
#
#     nodes_temp = Counter()
#     edges_out = []
#     nodes_out = []
#
#     for edge in sorted(edges.values(), key=lambda x: x['count'], reverse=True)[:n_edges]:
#         edges_out.append({'node1': edge['edge'][0].full_name, 'node2': edge['edge'][1].full_name,
#                           'docs': edge['count'], 'words': 0})
#
#         nodes_temp[edge['edge'][0]] += edge['count']
#         nodes_temp[edge['edge'][1]] += edge['count']
#
#     for node in nodes_temp:
#         nodes_out.append({'name': node.full_name, 'docs': nodes_temp[node], 'words': 0,
#                           'affiliation': node.most_likely_position})
#
#     store_network_for_visualization(nodes_out, edges_out, f'top_{n_edges}_edges',
#                                     f'top_{n_edges}_edges.json')

def generate_network_thedore_sterling():        # pylint: disable=C0103
    """
    Generate the network of Theodore Sterling, the largest recipient of CTR Special Project Grants
    For more on Stering, see http://tobacco-analytics.org/case/ctr
    """
    generate_people_network(names=['Theodor D. Sterling'], network_name='sterling',
                            max_number_of_nodes=100, include_2nd_degree_connections=True)


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
    people_db = PeopleDatabase()
    people_db.load_from_disk(Path(PEOPLE_DB_PATH))

    # load the whole 1970s network
    network = get_network_of_1970s_nodes_and_edges()
    edges = network['edges']

    org_counter = Counter()
    connection_counter = Counter()

    for edge in edges.values():
        person1, person2 = edge['edge']
        p1m = person1.most_likely_position.strip()
        p2m = person2.most_likely_position.strip()
        if (
                person1 and person2 and p1m != p2m and
                p1m != 'no positions available' and p2m != 'no positions available'
        ):
            org_counter[p1m] += edge['count']
            org_counter[p2m] += edge['count']
            connection_counter[tuple(sorted((p1m, p2m)))] += edge['count']

    nodes = {}
    edges = []

    for org, org_count in org_counter.most_common(200):
        nodes[org] = {'name': org, 'docs': org_counter[org], 'words': 0, 'affiliation': 'test'}

    for edge, edge_count in connection_counter.most_common():
        org1, org2 = edge
        if org1 in nodes and org2 in nodes:
            edges.append({'node1': org1, 'node2': org2, 'docs': edge_count, 'words': 0})

    nodes = sorted(nodes.values(), key=lambda x: x['docs'], reverse=True)

    store_network_for_visualization(nodes, edges,
                                    center_names=[], network_name='industry',
                                    file_name='whole_industry.json')

if __name__ == '__main__':

    # for match in search_possible_matches('KHAN').most_common(100):
    #     print()
    #     print(match[0].full_name, match[1])
    #     print(match[0].positions)
    #     print(match[0].aliases)

    # generate_network_of_1970s_nodes_and_edges()
    generate_network_lawyers()
    # generate_network_research_directors()
    # generate_network_thedore_sterling()
    # generate_network_whole_industry()
    # get_network_of_1970s_nodes_and_edges()
