"""
Models for the Rereading app.
"""
import json
from pathlib import Path
import pickle
from collections import Counter
import pandas as pd
from django.db import models
from name_disambiguation.person import Person
from name_disambiguation.name_preprocessing import parse_column_person
from name_disambiguation.config import DATA_PATH

from config.settings.base import BACKEND_DIR

MAX_LENGTH = 250


class DjangoPerson(models.Model):
    """Django database to represent Person objects
    Fields:
        last: CharField, last name
        first: CharField, first name
        middle: CharField, middle name
        full_name: CharField, '<first> <middle> <last>', is a unique field
        most_likely_org: CharField, org that appeared most times for the person
        positions: TextField, string json representation of positions Counter (all related
        annotations on the person). Use property positions_counter() to access!!
        aliases: TextField, string json representation of aliases Counter
        (all raw strings used to refer to this person). Use property aliases_counter() to access!!
        count: IntegerField, number of documents the person appeared in
    Properties:
        positions_counter: Counter of related annotations on the person
        aliases_counter: Counter of all raw strings used to refer to this person
    """
    last = models.CharField(max_length=MAX_LENGTH)
    first = models.CharField(max_length=MAX_LENGTH)
    middle = models.CharField(max_length=MAX_LENGTH)
    full_name = models.CharField(max_length=MAX_LENGTH, unique=True)
    most_likely_org = models.CharField(max_length=MAX_LENGTH)
    # positions & aliases are json strings that need to be parsed as Counter every time
    positions = models.TextField()
    aliases = models.TextField()
    count = models.IntegerField()

    def __str__(self):
        return self.full_name + ", Positions: " + str(self.positions) + ", Aliases: " + \
            str(self.aliases) + ", count: " + str(self.count)

    @property
    def positions_counter(self):
        """
        :return: positions Counter (from string json)
        """
        return Counter(json.loads(self.positions))

    @property
    def aliases_counter(self):
        """
        :return: aliases Counter (from string json)
        """
        return Counter(json.loads(self.aliases))


class Document(models.Model):
    """Django database to represent Person objects
    Fields:
        au: CharField, author(s)
        au_org: CharField, author organizations
        au_person: CharField, author(s)
        cc: CharField, cc-ed names
        cc_org: CharField, organization of cc-ed names
        collection: CharField, collection that the document was released from
        date: CharField, string representation of the date of the document
        doc_type: CharField, type of the document (e.g. letter, memo)
        pages: IntegerField, number of pages in document
        rc: CharField, recipient(s)
        rc_org: CharField, recipient organizations
        rc_person: CharField, recipient(s)
        text: TextField, text of the document
        tid: CharField, document ID
        title: CharField, title of the document

        authors: ManyToManyField, connect Document and its authors' DjangoPerson objects in database
        recipients: ManyToManyField, connect Document and its recipients' DjangoPerson objects in
        database
    """
    au = models.CharField(blank=True, max_length=MAX_LENGTH)        # pylint: disable=C0103
    au_org = models.CharField(blank=True, max_length=MAX_LENGTH)
    au_person = models.CharField(blank=True, max_length=MAX_LENGTH)
    cc = models.CharField(blank=True, max_length=MAX_LENGTH)        # pylint: disable=C0103
    cc_org = models.CharField(blank=True, max_length=MAX_LENGTH)
    collection = models.CharField(blank=True, max_length=MAX_LENGTH)
    date = models.CharField(blank=True, max_length=MAX_LENGTH)
    doc_type = models.CharField(blank=True, max_length=MAX_LENGTH)
    pages = models.IntegerField(blank=True)
    rc = models.CharField(blank=True, max_length=MAX_LENGTH)        # pylint: disable=C0103
    rc_org = models.CharField(blank=True, max_length=MAX_LENGTH)
    rc_person = models.CharField(blank=True, max_length=MAX_LENGTH)
    text = models.TextField(blank=True)
    tid = models.CharField(unique=True, max_length=MAX_LENGTH)
    title = models.CharField(blank=True, max_length=MAX_LENGTH)

    authors = models.ManyToManyField(DjangoPerson, related_name="document_by_authors")
    recipients = models.ManyToManyField(DjangoPerson, related_name="document_by_recipients")

    def __str__(self):
        return f'tid: {self.tid}, title: {self.title}, date: {self.date}'


def import_csv_to_document_model(csv_path):
    """
    Reads csv of docs and create Document model
    :param csv_path: Path to csv file
    :return: None
    """
    # Read csv into dataframe
    docs = pd.read_csv(csv_path).fillna('')
    # For each row, create & save the appropriate Document object
    for _, row in docs.iterrows():
        doc = Document(au=row['au'],
                       au_org=row['au_org'],
                       au_person=row['au_person'],
                       cc=row['cc'],
                       cc_org=row['cc_org'],
                       collection=row['collection'],
                       date=row['date'],
                       doc_type=row['doc_type'],
                       pages=int(row['pages']),
                       rc=row['rc'],
                       rc_org=row['rc_org'],
                       rc_person=row['rc_person'],
                       text=row['text'],
                       tid=row['tid'],
                       title=row['title'])
        doc.save()

        # for au/au_person, and rc/rc_person, parse it into list of individual raw names
        # assumes that names are either in 'au_person'/'rc_person or 'au'/'rc', but not both (
        # this is mostly true)
        # (if 'au_person' is not empty, then it only parses info from 'au_person'; otherwise,
        # parses 'au'; usually 'au_person' has more reliable information, 'au' may have erroneous
        # info. Same for rc)
        parsed_au = []
        if row['au_person']:
            parsed_au = parse_column_person(row['au_person'])
        elif row['au']:
            parsed_au = parse_column_person(row['au'])

        parsed_rc = []
        if row['rc_person']:
            parsed_rc = parse_column_person(row['rc_person'])
        elif row['rc']:
            parsed_rc = parse_column_person(row['rc'])

        def match_djangoperson_from_name(parsed_name):
            """
            Returns DjangoPerson object that contains parsed_name as an alias
            :param parsed_name: str, a parsed alias
            :return: DjangoPerson object
            """
            # Searches in database the DjangoPerson object whose aliases contain parsed_name
            try:
                # TODO: search for '"{name}"' [to include quotation marks in the search;
                #  currently if you search "Dunn WL", could match someone like "Pete-Dunn WLA"]
                name_with_quotes = f'\"{parsed_name}\"'
                person = DjangoPerson.objects.get(aliases__contains=name_with_quotes)
                print(person)
            # If no such DjangoPerson exists, create a new DjangoPerson from the parsed name and
            # store it in the database
            # TODO: currently after creating new DjangoPerson objects, there is no attempt to merge
            except DjangoPerson.DoesNotExist:
                person_original = Person(name_raw=parsed_name)
                person = DjangoPerson(last=person_original.last,
                                      first=person_original.first,
                                      middle=person_original.middle,
                                      full_name=f'{person_original.first} '
                                                f'{person_original.middle} {person_original.last}',
                                      most_likely_org=person_original.most_likely_org,
                                      # convert Counter object into json string
                                      positions=json.dumps(person_original.positions),
                                      aliases=json.dumps(person_original.aliases),
                                      count=person_original.count
                                      )
                person.save()
            # If multiple DjangoPerson objects are matched, return the first match and print out
            # message
            except DjangoPerson.MultipleObjectsReturned:
                person = DjangoPerson.objects.filter(aliases__contains=f'{parsed_name}')[0]
                print("Matched multiple DjangoPerson objects! Currently uses the first match")
            return person

        # for each raw author name, get the corresponding DjangoPerson object & add to the
        # Document model's authors (ManyToManyField)
        for name in parsed_au:
            # Currently this throws exception if it does not find exactly 1 matching object
            person = match_djangoperson_from_name(name.upper())
            doc.authors.add(person)

        # for each raw recipient name, get the corresponding DjangoPerson object & add to the
        # Document model's recipients (ManyToManyField)
        for name in parsed_rc:
            person = match_djangoperson_from_name(name.upper())
            doc.recipients.add(person)


def import_peopledb_to_person_model(file_path):
    """
    Import PeopleDatabase object from pickle file & store the corresponding DjangoPerson
    objects into database
    :param file_path: Path, file path to pickle file of PeopleDatabase
    :return:
    """
    # Load pickle file
    with open(str(file_path), 'rb') as infile:
        peopledb = pickle.load(infile)

    # For each Person in the PeopleDatabase, create the corresponding DjangoPerson & store
    for person in peopledb.people:
        person = DjangoPerson(last=person.last,
                              first=person.first,
                              middle=person.middle,
                              full_name=f'{person.first} {person.middle} {person.last}',
                              most_likely_org=person.most_likely_org,
                              # convert Counter object into json string
                              positions=json.dumps(person.positions),
                              aliases=json.dumps(person.aliases),
                              count=person.count)
        person.save()


# TODO update this / write interface between this and django models
class NetworkPerson:
    """
    Python class for representing people in the data;
    probably to be eventually replaced with a Django model
    """
    def __init__(self, pk: int, name: str, docs: int, words: int):
        self.pk = pk  # pylint: disable=C0103
        self.name = name
        self.docs = docs
        self.words = words


# TODO update this / write interface between this and django models
class NetworkEdge:
    """
    Python object to store edges, should be replaced if the Person class is replaced
    """
    def __init__(self, pk: int, node1: str, node2: str,  # pylint: disable-msg=R0913
                 docs: int, words: int):
        self.pk = pk  # pylint: disable=C0103
        self.node1 = node1  # could be replaced with Person
        self.node2 = node2
        self.docs = docs
        self.words = words


# TODO update this / write interface between this and django models
def load_network_json_data(return_type: str):
    """
    Loads test json data for initial prototyping
    :param return_type: string, determines which list needs to be determined, has the
    precondition that it either must be 'nodes' or 'edges'
    :return: list, contains all of the edges or all of the nodes (people at this point in time)
    from network_test_data.json
    """
    if return_type not in ['nodes', 'edges']:
        raise ValueError("Specified return type needs to be nodes or edges")

    json_path = Path(BACKEND_DIR, 'data', 'network_test_data.json')
    with open(json_path) as json_file:
        data = json.load(json_file)
    if return_type == "edges":
        edges = []
        for edges_dict in data['links']:
            pk = int(edges_dict.get('id'))  # pylint: disable=C0103
            node1 = edges_dict.get('node1')
            node2 = edges_dict.get('node2')
            docs = edges_dict.get('docs')
            words = int(edges_dict.get('words'))
            edges.append(NetworkEdge(pk, node1, node2, docs, words))
        return edges
    else:
        people = []
        for person_dict in data['nodes']:
            pk = int(person_dict.get('id'))  # pylint: disable=C0103
            name = person_dict.get('name')
            docs = person_dict.get('docs')
            words = int(person_dict.get('words'))
            people.append(NetworkPerson(pk, name, docs, words))
        return people


if __name__ == '__main__':
    peopledb_path = DATA_PATH / 'name_disambiguation' / 'names_db_10.pickle'
    docs_path = DATA_PATH / 'name_disambiguation' / 'dunn_docs.csv'
    import_peopledb_to_person_model(peopledb_path)
    import_csv_to_document_model(docs_path)
    Document.objects.all()
