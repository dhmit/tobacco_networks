"""
Views that define API endpoints for the site
"""
import json
from pathlib import Path

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from config.settings.base import BACKEND_DIR
from .serializers import PersonSerializer, EdgeSerializer
from .models import load_network_json_data


@api_view(['GET'])
def list_people(request):
    """
    Return a list of all Person objects, serialized.
    """
    serializer = PersonSerializer(instance=load_network_json_data("nodes"), many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_edges(request):
    """
    Return a list of all Edge objects, serialized.
    """
    serializer = EdgeSerializer(instance=load_network_json_data("edges"), many=True)
    return Response(serializer.data)


def get_network_data(request):
    """
    Temporary view to get network test data json
    """
    json_path = Path(BACKEND_DIR, 'data', 'network_test_data.json')
    with open(json_path) as json_file:
        data = json.load(json_file)

    return JsonResponse(data)
