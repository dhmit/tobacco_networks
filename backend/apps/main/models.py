"""
Models for the Rereading app.
"""
import json
from pathlib import Path
from django.db import models
import pandas as pd
import pickle
from collections import Counter

from config.settings.base import BACKEND_DIR


class Person:
    """
    Python class for representing people in the data;
    probably to be eventually replaced with a Django model
    """
    def __init__(self, pk: int, name: str, docs: int, words: int):
        self.pk = pk  # pylint: disable=C0103
        self.name = name
        self.docs = docs
        self.words = words

MAX_LENGTH = 250

class Document(models.Model):
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

    recipients = models.ManyToManyField(Person)
    authors = models.ManyToManyField(Person)

    def __str__(self):
        return f'tid: {self.tid}, title: {self.title}, date: {self.date}'

def import_csv_to_document_model(path):
    df = pd.read_csv(path).fillna('')
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

class Person(models.Model):
    # Maybe should be blank = True??
    last = models.CharField(max_length=255)
    first = models.CharField(max_length=255)
    middle = models.CharField(max_length=255)
    position = models.CharField(max_length=MAX_LENGTH)
    # TODO: Make counter into textfield as json
    positions = models.TextField()
    aliases = models.TextField()
    count = models.IntegerField()

    # TODO: write getter to parse json in textfield
    # See rereading/.../backend, analysis
    # Look into JSON Fields -- they won't work here, but it's
    # an example of how to do this stuff
    def get_parsed_positions(self):
        self.positions

    def __str__(self):
        s = f'{self.first} {self.middle} {self.last}'
        s = s + ", Position: " + str(self.positions) + ", Aliases: " + \
            str(self.aliases) + ", count: " + str(self.count)
        return s

    @property
    def positions_counter(self):
        return Counter(json.loads(self.positions))

    # TODO: write json getter here
    @property
    def aliases_list(self):

def import_peopledb_to_person_model(file_path):
    with open(str(file_path), 'rb') as infile:
        db = pickle.load(infile)
    for person in db.people:
        p = Person(last=person.last,
                   first=person.first,
                   middle=person.middle,
                   position=person.position,
                   positions=json.dumps(person.positions),
                   aliases=json.dumps(person.aliases),
                   count=person.count
                   )
        p.save()



class Edge:
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
            edges.append(Edge(pk, node1, node2, docs, words))
        return edges
    else:
        people = []
        for person_dict in data['nodes']:
            pk = int(person_dict.get('id'))  # pylint: disable=C0103
            name = person_dict.get('name')
            docs = person_dict.get('docs')
            words = int(person_dict.get('words'))
            people.append(Person(pk, name, docs, words))
        return people


if __name__ == '__main__':
    path = Path('..', 'data', 'name_disambiguation', 'dunn_docs.csv')
    import_csv_to_document_model(path)
    Document.objects.all()
