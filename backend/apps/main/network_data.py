

import json
from IPython import embed
from collections import Counter
import math


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
    if 'no positions available' in affiliations:
        no_pos_available_count = affiliations['no positions available']
        del affiliations['no positions available']

    most_common_affiliations = affiliations.most_common()[:8]

    if len(affiliations) > 8:
        others_group = set()
        others_group_count = 0
        for affiliation, aff_count in affiliations.most_common()[8:]:
            others_group.add(affiliation)
            others_group_count += aff_count

        most_common_affiliations += [('Others', others_group_count)]

    if no_pos_available_count > 0:
        most_common_affiliations += [('No Positions Available', no_pos_available_count)]

    clusters = {}
    current_unit_circle_pos_in_degrees = 0
    for affiliation_id, affiliation in enumerate(most_common_affiliations):
        affilation_name, affiliation_count = affiliation
        if affilation_name == 'no positions available':
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
            'y_pos': y_display_window
        }



        print(affilation_name)
        print(x_unit_circle, y_unit_circle)
        print(affiliation_center)
        print()

    embed()

if __name__ == '__main__':
    get_network_data()
