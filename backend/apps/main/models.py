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
    def __init__(self, id: int, name: str, docs: int, words: int):
        self.id = id
        self.name = name
        self.docs = docs
        self.words = words


def load_json_data():
    """
    Loads test json data for initial prototyping
    :return list, each person in the data as a Person object
    """
    JSON_PATH = Path(BACKEND_DIR, 'data', 'network_test_data.json')
    with open(JSON_PATH) as json_file:
        data = json.load(json_file)
    person_dicts = data['nodes']
    people = []
    for person_dict in person_dicts:
        id = int(person_dict.get('id'))
        name = person_dict.get('name')
        docs = person_dict.get('docs')
        words = int(person_dict.get('words'))
        person_obj = Person(id, name, docs, words)
        people.append(person_obj)
    return people
