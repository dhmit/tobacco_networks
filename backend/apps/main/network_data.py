

import json
from IPython import embed
from collections import Counter
import math
import brewer2mpl


def get_network_data():

    json_path = '/home/stephan/tobacco/code/tobacco_networks/backend/data/person_lawyers.json'
    with open(json_path) as json_file:
        data = json.load(json_file)
    nodes = data['nodes']

    affiliations = Counter()

    for node in nodes:
        affiliations[node['affiliation']] += 1

    # idea: each group takes up space proportionally on a 360 degree unit circle
    # the goal is to calculate where the center of each node cluster is on the unit circle
    no_pos_available_count = 0
    if 'No Positions Available' in affiliations:
        no_pos_available_count = affiliations['No Positions Available']
        del affiliations['No Positions Available']

    most_common_affiliations = affiliations.most_common()[:8]

    # if more than 8 affiliations, put the ones outside the top 8 into an "others" group
    others_group = set()
    if len(affiliations) > 8:
        others_group_count = 0
        for affiliation, aff_count in affiliations.most_common()[8:]:
            others_group.add(affiliation)
            others_group_count += aff_count

        most_common_affiliations += [('Others', others_group_count)]

    if no_pos_available_count > 0:
        most_common_affiliations += [('No Positions Available', no_pos_available_count)]

    clusters = {}
    current_unit_circle_pos_in_degrees = 0
    bmap = brewer2mpl.get_map(name='Spectral', map_type='Diverging',
                              number=len(most_common_affiliations))
    for affiliation_id, affiliation in enumerate(most_common_affiliations):
        affilation_name, affiliation_count = affiliation
        if affilation_name == 'No Positions Available':
            continue
        total_degrees_taken_by_affiliation = affiliation_count / len(nodes) * 360
        affiliation_center = current_unit_circle_pos_in_degrees + \
                             total_degrees_taken_by_affiliation / 2
        current_unit_circle_pos_in_degrees += total_degrees_taken_by_affiliation


        x_unit_circle = math.sin(affiliation_center * math.pi/180)
        y_unit_circle = math.cos(affiliation_center * math.pi/180)

        x_display_window = 0.5 - 0.5 * x_unit_circle
        y_display_window = 0.5 - 0.5 * y_unit_circle


        clusters[affiliation_id] = {
            'id': affiliation_id,
            'name': affilation_name,
            'count': affiliation_count,
            'x_pos': x_display_window,
            'y_pos': y_display_window,
            'color': bmap.colors[affiliation_id]
        }

    # assign each node to a cluster.
    # first create a map from affiliation to cluster

    affiliation_to_cluster_dict = {
        'No Positions Available': len(clusters) -1
    }
    for affiliation in others_group:
        # id of "Others" is the second to last cluster
        affiliation_to_cluster_dict[affiliation] = len(clusters) -2
    for cluster in clusters.values():
        affiliation_to_cluster_dict[cluster['name']] = cluster['id']

    embed()
    for node in nodes:
        node['cluster'] = affiliation_to_cluster_dict[node['affiliation']]
    embed()

if __name__ == '__main__':
    get_network_data()
