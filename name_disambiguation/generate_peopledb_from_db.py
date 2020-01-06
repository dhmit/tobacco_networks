from tobacco.utilities.databases import Database

import json
import pickle
from collections import Counter
from pathlib import Path
import re

from IPython import embed

import pandas as pd

from name_disambiguation.name_preprocessing import parse_column_person, parse_column_org
from name_disambiguation.people_db import PeopleDatabase
from name_disambiguation.config import COMPANY_ABBREVIATIONS_TO_SKIP
from name_disambiguation.person import Person

from name_disambiguation.clean_org_names import RAW_ORG_TO_CLEAN_ORG_DICT


from name_disambiguation.name_preprocessing import parse_column_person

DOCS_CSV_PATH = Path('..', 'data', 'documents', 'docs_1970s_all.csv')
NETWORK_PATH = Path('..', 'data', 'network_generation', 'network_1970s.pickle')
PEOPLE_DB_PATH = Path('..', 'data', 'network_generation', '1970s_from_csv.pickle')
NAMES_TO_SKIP = {
    'American Brands Inc',
    'Hardy Shook',
    'Shook Hardy',
}

def create_db_of_1970s_docs_from_csv():
    """
    We have this strange 1970s db from November 2019 but I don't know how it was created.
    This script simply uses the docs_1970s_all.csv to create a people_db using the info found in
    those documents.

    :return:
    """

    print("Generating new 1970s People DB")

    df = pd.read_csv(DOCS_CSV_PATH).fillna('')  # pylint: disable=C0103
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


def get_network_of_1970s_nodes_and_edges():

    try:
        with open(NETWORK_PATH, 'rb') as infile:
            return pickle.load(infile)
    except FileNotFoundError:


        people_db = PeopleDatabase()
        try:
            people_db.load_from_disk(PEOPLE_DB_PATH)
        except FileNotFoundError:
            create_db_of_1970s_docs_from_csv()
            people_db.load_from_disk(PEOPLE_DB_PATH)


        df = pd.read_csv(DOCS_CSV_PATH).fillna('')  # pylint: disable=C0103

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
                author.docs_authored.append(doc)
                if author in nodes:
                    nodes[author]['count_authored'] += 1
                else:
                    embed()
                    nodes[author] = {'person': author, 'docs_authored': {}, 'count_received': 0}

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
    edges_out = []
    nodes_out = []

    c = Counter()

    # first identify all the primary edges including at least one person from center_people
    for idx, edge in enumerate(edges.values()):

        person1 = people_db.get_person_from_alias(edge['edge'][0].aliases.most_common(1)[0][0])
        person2 = people_db.get_person_from_alias(edge['edge'][1].aliases.most_common(1)[0][0])

        if not person1 or not person2:
            embed()
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

    # store all people in the network to be displayed in their own network
    new_people_db = PeopleDatabase()
    for node, node_count in nodes_temp.most_common(max_number_of_nodes):
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



def parse_authors_or_recipients_of_doc(side, doc, counters, people_db):

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

        except:
            counters['error'][name] += 1

    return doc_people, doc_organizations

def parse_au_or_rc_organizations_of_doc(side, doc, counters, people_db):

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

                if org == 'Hetsko, Cyril F':
                    embed()

    return organizations


def check_if_name_looks_like_an_organization(name):
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



if __name__ == '__main__':

    # generate_network_of_1970s_nodes_and_edges()
    generate_network_lawyers()
    # generate_network_research_directors()


