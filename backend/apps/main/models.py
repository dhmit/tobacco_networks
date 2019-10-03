"""
Models for the Rereading app.
"""
import json
from pathlib import Path
# from django.db import models

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


def load_json_data():
    """
    Loads test json data for initial prototyping
    :return list, each person in the data as a Person object
    """
    # TODO: change this function name to be more descriptive
    json_path = Path(BACKEND_DIR, 'data', 'network_test_data.json')
    with open(json_path) as json_file:
        data = json.load(json_file)
    person_dicts = data['nodes']
    people = []
    for person_dict in person_dicts:
        pk = int(person_dict.get('id'))  # pylint: disable=C0103
        name = person_dict.get('name')
        docs = person_dict.get('docs')
        words = int(person_dict.get('words'))
        person_obj = Person(pk, name, docs, words)
        people.append(person_obj)
    return people


class Edge:
    """
    Python object to store edges, should be replaced if the Person class is replaced
    """
    def __init__(self, pk: int, node1: str, node2: str, docs: int, words: int):
        self.pk = pk
        self.node1 = node1  # could be replaced with Person
        self.node2 = node2
        self.docs = docs
        self.words = words


def load_json_data_edge():
    """
    Loads test json data for initial prototyping
    :return: list, each edge in the data as an Edge object
    """
    json_path = Path(BACKEND_DIR, 'data', 'network_test_data.json')
    with open(json_path) as json_file:
        data = json.load(json_file)
    edges_dicts = data['links']
    edges = []
    for edges_dict in edges_dicts:
        pk = int(edges_dict.get('id'))
        node1 = edges_dict.get('node1')
        node2 = edges_dict.get('node2')
        docs = int(edges_dict.get('docs'))
        words = int(edges_dict.get('words'))
        edge_obj = Edge(pk, node1, node2, docs, words)
        edges.append(edge_obj)
    return edges
