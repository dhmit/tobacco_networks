"""
Views that define API endpoints for the site
"""
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import PersonSerializer
from .models import load_json_data


@api_view(['GET'])
def list_people(request):
    """
    Return a list of all Person objects, serialized.
    """
    serializer = PersonSerializer(instance=load_json_data(), many=True)
    return Response(serializer.data)
