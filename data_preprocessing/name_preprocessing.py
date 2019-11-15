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
from clean_org_names import RAW_ORG_TO_CLEAN_ORG_DICT
from IPython import embed


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


def generate_network(main_name='DUNN,WL', people_db_path='people_db_1970s.pickle',
                     docs_csv_path=Path('..', 'data', 'documents', 'docs_1970s_all.csv')):


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
                nodes[recipient] = {'person': recipient, 'count_authored': 0, 'count_received': 1}

        for author in doc_authors:
            for recipient in doc_recipients:
                edge = tuple(sorted([author, recipient]))
                if edge in edges:
                    edges[edge]['count'] += 1
                else:
                    edges[edge] = {'edge': edge, 'count': 1}

    embed()
    network = {
        'nodes': nodes,
        'edges': edges
    }
    pickle.dump


    ec = Counter()
    for edge in edges:
        ec[edge] = edges[edge]['count']
    nc = Counter()
    for node in nodes:
        nc[node] = nodes[node]['count_authored']

    # nodes_temp = Counter()
    # edges_out = []
    # nodes_out = []
    # for edge in edges:
    #     if edges[edge]['count'] > 300:
    #         edges_out.append({'node1': edge[0].full_name, 'node2': edge[1].full_name,
    #                           'docs': edges[edge]['count'], 'words': 20})
    #         nodes_temp[edge[0]] += edges[edge]['count']
    #         nodes_temp[edge[1]] += edges[edge]['count']
    #
    # for node in nodes_temp:
    #     node.set_likely_position()
    #     print(node.most_likely_org)
    #     nodes_out.append({'name': node.full_name, 'docs': nodes_temp[node], 'words': 20,
    #                       'affiliation': node.most_likely_org})

    nodes_out = []
    edges_out = []
    most_frequent_nodes = set([n[0] for n in nc.most_common(300)])
    for node in most_frequent_nodes:
        node.set_likely_position()
        nodes_out.append({'name': node.full_name, 'docs': nodes[node]['count_authored'], 'words': 20,
                          'affiliation': node.most_likely_org})

    for edge in edges:
        if (people_db.alias_to_person_dict['HOYT,WT'] == edge[0] and
            people_db.alias_to_person_dict['WAKEHAM,H'] == edge[1]):
            embed()
        if edge[0] in most_frequent_nodes and edge[1] in most_frequent_nodes:
            edges_out.append({'node1': edge[0].full_name, 'node2': edge[1].full_name,
                              'docs': edges[edge]['count'], 'words': 20})


    import json
    network = {
        'nodes': nodes_out,
        'links': edges_out
    }
    with open('network_test_data_top_300_nodes.json', 'w') as out:
        json.dump(network, out)



    embed()





def parse_doc_metadata_csv_to_people_db(csv_path, people_db=None, output_people_db_path=None):
    """
    Parses the metadata for each document in a csv of tobacco document metadata

    For each document belonging to a certain company,
    finds Person that that document author alias maps to,
    and adds that company to the position counter of that Person

     Goes through documents and updates authors/recipients' positions
     based on organization associated with document

     Adds people to db_current if their alias is associated with a doc but is not in
     db_current yet

     Ignores:
         organizations not in RAW_ORG_TO_CLEAN_ORG_DICT
         docs with more than 1 organization
         docs with more than 4 recipients
         docs with no people associated with them


    :param csv_path: Path
    :param people_db: PeopleDatabase that information will be added to
    :return:
    """

    if not people_db:
        people_db = PeopleDatabase()

    # get lists of dicts for authors and recipients. each of them has 3 fields:
    # general, person, organization
    people_dicts = get_au_and_rc_by_document(csv_path, return_type='both')

    print(len(people_dicts))
    for idx, person in enumerate(people_dicts):
        if idx % 100 == 0:
            print(idx, len(people_db))

        orgs = set()
        for org in person['organization']:
            if org not in RAW_ORG_TO_CLEAN_ORG_DICT:
                continue
            orgs.add(RAW_ORG_TO_CLEAN_ORG_DICT[org])

        if len(orgs) == 0:
            org = None
        else:
            org = list(orgs)[0]

        aliases = person['person'] + person['general']
        if not aliases or len(aliases) >= 4:
            continue

        for alias in aliases:
            people_db.add_person_raw(alias, position=org)

    people_db.merge_duplicates()

    if output_people_db_path:
        people_db.store_to_disk(output_people_db_path)

    return people_db


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


class TestAddPositions(unittest.TestCase):
    """Tests adding positions to people in a people database
    Attributes:
        people_db: an expected people database
    """
    def setUp(self):
        self.people_db = PeopleDatabase()
        for name in ['Dunn, WL', 'Garcia, Raquel', 'Risi, Stephan']:
            self.people_db.add_person_raw(name, 1)

    def test_parse_doc_metadata_csv(self):
        """
        Test add_au_and_rc_function
        """
        csv_path = Path('..', 'data', 'name_disambiguation', 'test_docs.csv')
        parse_doc_metadata_csv(csv_path, people_db=self.people_db)

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

        self.assertEqual(self.people_db, expected_people_db)


if __name__ == '__main__':
#    unittest.main()
    csv_path = Path('..', 'data', 'documents', 'docs_1970s_all.csv')
#    csv_path = Path('..', 'data', 'documents', 'docs_1970s_5k.csv')

    generate_network()
#    db = parse_doc_metadata_csv(csv_path)
    embed()
