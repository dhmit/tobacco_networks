"""
Helper file, currently makes path to DATA_PATH and BACKEND_PATH available

"""

import os
from pathlib import Path

DATA_PATH = Path(Path(os.path.abspath(os.path.dirname(__file__))).parent, 'data')


MANUALLY_MERGED_NAMES = [
    {
        'authoritative_name': {'last': 'Ahrensfeld', 'first': 'Thomas', 'middle': 'F'},
        'aliases_to_merge': ['AHRENSFELD,TF', 'AHRENSFELD,T']
    },
    {
        'authoritative_name': {'last': 'Bryant', 'first': 'H', 'middle': 'DeBaun'},
        'aliases_to_merge': ['Bryant, H', 'BRYANT,D', 'Bryant, DeBaun', 'BRYANT,HD']
    },
    {
        'authoritative_name': {'last': 'Haas', 'first': 'Frederick', 'middle': 'P',
                               'affiliation': 'Liggett & Myers'},
        'aliases_to_merge': ['Haas, F', 'HAAS,FP', 'HAAS FP, LM']
    },
    {
        'authoritative_name': {'last': 'Hardy', 'first': 'David', 'middle': 'Ross'},
        'aliases_to_merge': ['HARDY,DR', 'Hardy, D', 'HARDY,DR/SHOOK, HARDY & BACON',
                             'Hardy-DR, Shook Hardy']
    },
    {
        'authoritative_name': {'last': 'Hetsko', 'first': 'Cyril', 'middle': 'F'},
        'aliases_to_merge': ['Hetsko-CF', 'Hetsko-CF, American Brands Inc',
                             'HETSKO CF, AMER BRANDS', 'Hetsko-CF American Brands Inc',
                             'Hetsko, C', 'Hetsko-CF, American Brands']
    },
    {
        'authoritative_name': {'last': 'Holtzman', 'first': 'Alexander', 'middle': ''},
        'aliases_to_merge': ['HOLTZMAN,A', 'Holtzman, Alexander',
                             'Holtzmann, Alexander [Privlog:] HOLTZMAN,A']
    },
    {
        'authoritative_name': {'last': 'Hughes', 'first': 'Ivor', 'middle': 'Wallace'},
        'aliases_to_merge': ['HUGHES,IW', 'Hughes-I', 'HUGHES,IW/X']
    },
    {
        'authoritative_name': {'last': 'Senkus', 'first': 'Murray', 'middle': ''},
        'aliases_to_merge': ['SENKUS M', 'Senkus, Murray']
    },
    {
        'authoritative_name': {'last': 'Ramm', 'first': 'Henry', 'middle': 'H'},
        'aliases_to_merge': ['RAMM HH', 'RAMM H, CTR', 'Ramm-HH Council For Tobacco Research']
    },

    {
        'authoritative_name': {'last': 'Roemer', 'first': 'Henry', 'middle': 'C',
                               'affiliation': "R.J. Reynolds"},
        'aliases_to_merge': ['ROEMER HC JR', 'Roemer, H']
    },
    {
        'authoritative_name': {'last': 'Shinn', 'first': 'William', 'middle': 'W'},
        'aliases_to_merge': ['SHINN,WW', 'SHINN,W', 'SHINN,WW/SHOOK, HARDY & BACON',
                             'Shinn-WW, Shook Hardy']
    },
    {
        'authoritative_name': {'last': 'Teague', 'first': 'Claude', 'middle': 'Edward',
                               'affiliation': "R.J. Reynolds"},
        'aliases_to_merge': ['TEAGUE CE JR', 'TEAGUE,C']
    },
    {
        'authoritative_name': {'last': 'Wakeham', 'first': 'Helmut', 'middle': 'R'},
        'aliases_to_merge': ['WAKEHAM,H', 'WAKEHAM,HR']
    },
    {
        'authoritative_name': {'last': 'Yeaman', 'first': 'Addison', 'middle': 'Y'},
        'aliases_to_merge': ['YEAMAN,A', 'YEAMAN AY, CTR', 'YEAMAN,A/X', 'Yeaman, Addison']
    },
]
