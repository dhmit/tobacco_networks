"""
Views that define API endpoints for the site
"""
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PersonSerializer
from .models import load_json_data


class ListPeople(APIView):
    """
    View to list all people in the network.
    """

    # noinspection PyMethodMayBeStatic
    def get(self, _request):
        """
        Return a list of all Person objects, serialized.
        """
        serializer = PersonSerializer(instance=load_json_data(), many=True)
        return Response(serializer.data)
