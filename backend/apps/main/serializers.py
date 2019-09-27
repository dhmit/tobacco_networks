"""
Serializers take models or other data structures and present them
in ways that can be transported across the backend/frontend divide, or
allow the frontend to suggest changes to the backend/database.
"""
from rest_framework import serializers


class PersonSerializer(serializers.Serializer):
    """
    Serializer for the Person model
    """
    pk = serializers.IntegerField(read_only=True)  # pylint: disable=C0103
    name = serializers.CharField(read_only=True)
    docs = serializers.IntegerField(read_only=True)
    words = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        """ We will not create new objects using this serializer """

    def update(self, instance, validated_data):
        """ We will not update data using this serializer """
