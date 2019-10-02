"""
Views that define API endpoints for the site
"""
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import PersonSerializer, EdgeSerializer
from .models import load_json_data, load_json_data_edge


@api_view(['GET'])
def list_people(request):
    """
    Return a list of all Person objects, serialized.
    """
    serializer = PersonSerializer(instance=load_json_data(), many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_edges(request):
    """
    Return a list of all Edge objects, serialized.
    """
    serializer = EdgeSerializer(instance=load_json_data_edge(), many=True)
    return Response(serializer.data)
