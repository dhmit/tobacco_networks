import json
from pathlib import Path

from name_preprocessing import get_au_and_rc_by_document, get_clean_org_names
from people_db import PeopleDatabase

# dict that converts raw organization names to clean, official organization names
RAW_ORG_TO_CLEAN_ORG_DICT = get_clean_org_names()


def merge_names_from_file(name_file=Path('..', 'data', 'name_disambiguation',
                                         'tobacco_names_raw_test_small.json')):
    """
    Creates a people db from reading json file (dict of raw names and counts) and merges people
    in it. Stores people db in a pickle file
    :param name_file:
    :return:
    """

    with open(name_file, 'r') as infile:
        name_dict = json.load(infile)

    import time
    s = time.time()

    # add everyone to a PeopleDatabase
    people_db = PeopleDatabase()
    for name in name_dict:
        if name_dict[name] >= 3:
            people_db.add_person_raw(name_raw=name, count=name_dict[name])

    print("Length: ", len(people_db))

    # then merge the duplicate / similar names
    people_db.create_positions_csv()
    people_db.merge_duplicates()

    people_db.store_to_disk(Path('names_db_3.pickle'))
    print("Merging names took", time.time() - s)

#    with open('alias_to_name.json', 'w') as outfile:
#        json.dump(people_db.get_alias_to_name(), outfile)


def add_au_and_rc_org(db_to_add, path):
    """
    Input are a people database and a path to a document
    Returns None

    For each document belonging to a certain company,
    finds Person that that document author alias maps to,
    and adds that company to the position counter of that Person

    :param db_to_add: a PeopleDatabase, path: path to authors/orgs document
    :param path: file path to the docs csv file that includes au_org & rc_org
    :return: None
    """

    alias_to_person_dict = db_to_add.get_alias_to_person_dict()

    def update_au_and_rc_positions(db_current, au_or_rc, relevant_dicts):
        """
        Goes through documents and updates authors/recipients' positions
        based on organization associated with document

        Adds people to db_current if their alias is associated with a doc but is not in
        db_current yet

        Ignores:
            organizations not in RAW_ORG_TO_CLEAN_ORG_DICT
            docs with more than 1 organization
            docs with more than 4 recipients
            docs with no people associated with them

        :param db_current: People Database
        :param au_or_rc: string ('au' or 'rc')– specifies whether we're looking at authors or
        recipients
        :param relevant_dicts: 2 item list, 1st = dict with authors and organizations, by doc,
        2nd = dict of recipients and organizations by doc.
        :return: None
        """
        if au_or_rc == 'au':
            relevant_person = 'au_person'
            relevant_org = 'au_org'
        else:
            relevant_person = 'rc_person'
            relevant_org = 'rc_org'

        for doc in relevant_dicts:
            orgs = set()
            for org in doc[relevant_org]:
                if org not in RAW_ORG_TO_CLEAN_ORG_DICT:
                    continue
                else:
                    orgs.add(RAW_ORG_TO_CLEAN_ORG_DICT[org])

            if len(orgs) != 1:
                continue
            else:
                org = list(orgs)[0]
                aliases = doc[relevant_person]
                aliases.extend(doc[au_or_rc])
                if au_or_rc == 'rc' and len(aliases) >= 5:
                    continue
                if not aliases:
                    continue
                for alias in aliases:
                    if alias not in alias_to_person_dict:
                        db_current.add_person_raw(alias)
                    else:
                        alias_to_person_dict[alias].positions[org] += 1

    au_dicts, rc_dicts = get_au_and_rc_by_document(path)
    update_au_and_rc_positions(db_to_add, 'au', au_dicts)
    update_au_and_rc_positions(db_to_add, 'rc', rc_dicts)


if __name__ == '__main__':
    pass
