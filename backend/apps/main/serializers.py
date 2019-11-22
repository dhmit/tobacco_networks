"""
Serializers take models or other data structures and present them
in ways that can be transported across the backend/frontend divide, or
allow the frontend to suggest changes to the backend/database.
"""
import json
from pathlib import Path
from rest_framework import serializers
from .models import Person


class EdgeSerializer(serializers.Serializer):
    """
    Serializer for the Edge model
    """
    pk = serializers.IntegerField(read_only=True)  # pylint: disable=C0103
    node1 = serializers.CharField(read_only=True)
    node2 = serializers.CharField(read_only=True)
    docs = serializers.IntegerField(read_only=True)
    words = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        """ We will not create new objects using this serializer """

    def update(self, instance, validated_data):
        """ We will not update data using this serializer """


class PersonInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Person Info model
    """
    class Meta:
        model = Person
        fields = ["last", "first", "middle", "full_name", "most_likely_org", "positions",
                  "aliases", "count"]

    def create(self, validated_data):
        """ We will not create new objects using this serializer """

    def update(self, instance, validated_data):
        """ We will not update data using this serializer """


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

    json_path = Path('/Users/kimba/Documents/GitHub/tobacco_networks/backend', 'data',
                     'network_test_data.json')
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
