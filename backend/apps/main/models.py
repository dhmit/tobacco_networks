"""
Models for the Rereading app.
"""
import json
from pathlib import Path
from django.db import models
import pandas as pd
import pickle
from collections import Counter
from name_disambiguation.person import Person
from name_disambiguation.people_db import PeopleDatabase
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
        most_likely_org: CharField, org that appeared most times for the person
        positions: TextField, string json representation of positions Counter (all related
        annotations on the person). DO NOT DIRECTLY ACCESS (use property positions_counter)
        aliases: TextField, string json representation of aliases Counter
        (all raw strings used to refer to this person). DO NOT DIRECTLY ACCESS (use property
        aliases_counter)
        count: IntegerField, number of documents the person appeared in
    Properties:
        positions_counter: Counter of related annotations on the person
        aliases_counter: Counter of all raw strings used to refer to this person
    """
    # Maybe should be blank = True??
    last = models.CharField(max_length=255)
    first = models.CharField(max_length=255)
    middle = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, default=None, unique=True)
    most_likely_org = models.CharField(max_length=MAX_LENGTH)
    # positions & aliases are json strings that need to be parsed as Counter every time
    positions = models.TextField()
    aliases = models.TextField()
    count = models.IntegerField()

    def __str__(self):
        s = f'{self.first} {self.middle} {self.last}'
        s = s + ", Positions: " + str(self.positions) + ", Aliases: " + \
            str(self.aliases) + ", count: " + str(self.count)
        return s

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
    # TODO: check if the field descriptions are correct
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
        text: TextField, text of the document (is it full text??)
        tid: CharField, document ID
        title: CharField, title of the document

        authors: ManyToManyField, connect Document and its authors' Person objects in Django
        recipients: ManyToManyField, connect Document and its recipients' Person objects in Django
    """
    au = models.CharField(blank=True, max_length=MAX_LENGTH)
    au_org = models.CharField(blank=True, max_length=MAX_LENGTH)
    au_person = models.CharField(blank=True, max_length=MAX_LENGTH)
    cc = models.CharField(blank=True, max_length=MAX_LENGTH)
    cc_org = models.CharField(blank=True, max_length=MAX_LENGTH)
    collection = models.CharField(blank=True, max_length=MAX_LENGTH)
    date = models.CharField(blank=True, max_length=MAX_LENGTH)
    doc_type = models.CharField(blank=True, max_length=MAX_LENGTH)
    pages = models.IntegerField(blank=True)
    rc = models.CharField(blank=True, max_length=MAX_LENGTH)
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
    :return:
    """
    df = pd.read_csv(csv_path).fillna('')
    for _, row in df.iterrows():
        d = Document(au=row['au'],
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
                     title=row['title']
                     )
        d.save()

        # for au/au_person, and rc/rc_person, parse it into list of individual raw names
        parsed_au = []
        if row['au_person']:
            parsed_au = parse_column_person(row['au_person'])
        elif row['au']:
            parsed_au = parse_column_person(row['au'])
        # for each raw name, search in Person model by aliases
        # add connection to authors (ManyToManyField)
        for name in parsed_au:
            # Currently this throws exception if it does not find exactly 1 matching object
            person = DjangoPerson.objects.get(aliases__contains=name)
            d.authors.add(person)

        parsed_rc = []
        if row['rc_person']:
            parsed_rc = parse_column_person(row['rc_person'])
        elif row['rc']:
            parsed_rc = parse_column_person(row['rc'])
        for name in parsed_rc:
            # Currently this throws exception if it does not find exactly 1 matching object
            try:
                # TODO: figure out why can't search for f'"{name}"' [currently if you search
                #  "Dunn WL", could potentially match someone like "Pete-Dunn WLA"]
                person = DjangoPerson.objects.get(aliases__contains=f'"{name}"')
            except DjangoPerson.DoesNotExist:
                person_original = Person(name_raw=name)
                person = DjangoPerson(last=person_original.last,
                                      first=person_original.first,
                                      middle=person.middle,
                                      full_name=f'{person.first} {person.middle} {person.last}',
                                      most_likely_org=person.most_likely_org,
                                      # convert Counter object into json string
                                      positions=json.dumps(person.positions),
                                      aliases=json.dumps(person.aliases),
                                      count=person.count
                                      )
            d.recipients.add(person)


def import_peopledb_to_person_model(file_path):
    with open(str(file_path), 'rb') as infile:
        db = pickle.load(infile)

    for person in db.people:
        p = DjangoPerson(last=person.last,
                         first=person.first,
                         middle=person.middle,
                         full_name=f'{person.first} {person.middle} {person.last}',
                         most_likely_org=person.most_likely_org,
                         # convert Counter object into json string
                         positions=json.dumps(person.positions),
                         aliases=json.dumps(person.aliases),
                         count=person.count
                         )
        p.save()


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
