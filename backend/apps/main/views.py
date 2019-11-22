"""
Views that define API endpoints for the site
"""
import json
from pathlib import Path

import random

from django.http import JsonResponse
from backend.config.settings.base import BACKEND_DIR


def get_network_data(request):
    """
    Temporary view to get network test data json
    """
    json_path = Path(BACKEND_DIR, 'data', 'network_test_data.json')
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
    for link in links:
        link['source'] = link['node1']
        link['target'] = link['node2']
    return JsonResponse(data)
