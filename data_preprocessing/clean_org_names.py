"""
Contains helper function to get RAW_ORG_TO_CLEAN_ORG_DICT (convert raw org names to clean names)
"""
from pathlib import Path
import json


def get_clean_org_names():
    """
    :return: dict, maps official organization names to all their variants
    """
    # read clean_org_names
    file_name = Path('..', 'data', 'name_disambiguation', 'clean_org_names_to_raw_org_names.json')
    with open(file_name, 'r') as infile:
        name_dict = json.load(infile)

    # invert dict
    inv_name_dict = {}
    for official in name_dict:
        for j in name_dict[official]:
            inv_name_dict[j] = official
        inv_name_dict[official] = official
    return inv_name_dict


RAW_ORG_TO_CLEAN_ORG_DICT = get_clean_org_names()
