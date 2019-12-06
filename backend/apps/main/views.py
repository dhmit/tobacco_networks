"""
Views that define API endpoints for the site
"""
import json
from pathlib import Path

import random
from collections import Counter
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from backend.config.settings.base import BACKEND_DIR


def get_network_data(request):
    """
    Temporary view to get network test data json
    """

    datasets = {
        'lawyers': 'person_lawyers.json',
        'research_directors': 'person_research_directors.json',
        'sterling': 'person_sterling.json',
        'top_100_edges': 'top_100_edges.json',
        'test': 'network_test_data.json'
    }

    if request.GET and 'dataset' in request.GET:
        json_filename = datasets[request.GET['dataset']]
    else:
        json_filename = 'network_test_data.json'

    json_path = Path(BACKEND_DIR, 'data', json_filename)
    with open(json_path) as json_file:
        data = json.load(json_file)
    nodes = data['nodes']
    for node in nodes:
        node['x'] = random.random()*500
        node['y'] = random.random()*500
        node['weight'] = node['docs']
        node['affiliation'] = random.choice(['Phillip Morris International', 'British American '
                                                                             'Tobacco',
                                             'Japan Tobacco', 'Imperial Tobacco'])
    links = data['links']
    adjacent_nodes = {}
    for link in links:
        link['source'] = link['node1']
        link['target'] = link['node2']
        adjacent_nodes[link['node1'] + "-" + link['node2']] = True
        adjacent_nodes[link['node2'] + "-" + link['node1']] = True
    data["adjacent_nodes"] = adjacent_nodes

    # TODO: Need to add adjacent_nodes and add False value : talk to rest of group about this

    return JsonResponse(data)


@api_view(['GET'])
def get_person_info(request):
    """
    Finds a person matching the full name requested by the user, serializes this person, and
    returns the serialized person
    :param request: request from the user;
        request.query_params is a dict {'full name': FULL NAME OF RELEVANT PERSON}
    :return: serialized person matching full name imbain request
    """
    queryset = DjangoPerson.objects.filter(full_name=request.query_params['full_name'])
    if not list(queryset):
        full_name = request.query_params['full_name']
        new = DjangoPerson(
            last="",
            first="",
            middle="",
            full_name=full_name + " not available.",
            most_likely_org="",
            positions=json.dumps(Counter()),
            aliases=json.dumps(Counter()),
            count=0)
        serializer = PersonInfoSerializer(instance=new, many=False)
        return Response(serializer.data)
    else:
        serializer = PersonInfoSerializer(instance=queryset, many=True)
        return Response(serializer.data)
