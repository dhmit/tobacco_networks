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
        edges_dicts = data['links']
        edges = []
        for edges_dict in edges_dicts:
            pk = int(edges_dict.get('id'))  # pylint: disable=C0103
            node1 = edges_dict.get('node1')
            node2 = edges_dict.get('node2')
            docs = edges_dict.get('docs')
            words = int(edges_dict.get('words'))
            edge_obj = Edge(pk, node1, node2, docs, words)
            edges.append(edge_obj)
        return edges
    else:
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
