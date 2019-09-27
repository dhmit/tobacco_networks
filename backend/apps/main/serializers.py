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
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    docs = serializers.IntegerField(read_only=True)
    words = serializers.IntegerField(read_only=True)
