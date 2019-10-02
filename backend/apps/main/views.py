"""
Views that define API endpoints for the site
"""
import json
from pathlib import Path
from config.settings.base import BACKEND_DIR

from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import JsonResponse

from .serializers import PersonSerializer
from .models import load_json_data


@api_view(['GET'])
def list_people(request):
    """
    Return a list of all Person objects, serialized.
    """
    serializer = PersonSerializer(instance=load_json_data(), many=True)
    return Response(serializer.data)


def get_network_data(request):
    """
    Temporary view to get network test data json
    """
    json_path = Path(BACKEND_DIR, 'data', 'network_test_data.json')
    with open(json_path) as json_file:
        data = json.load(json_file)

    return JsonResponse(data)

