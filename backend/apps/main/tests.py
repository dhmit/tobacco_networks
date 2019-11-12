"""
Tests for the main app.
"""

from django.test import TestCase
import json
from pathlib import Path
from django.db import models
import pandas as pd
import pickle
from collections import Counter
from name_disambiguation.person import Person
from name_disambiguation.people_db import PeopleDatabase
from name_disambiguation.name_preprocessing import parse_column_person
from name_disambiguation.config import DATA_PATH
from apps.main.models import DjangoPerson
from apps.main.models import Document
from apps.main.models import import_peopledb_to_person_model

class MainTests(TestCase):
    def setUp(self):
        # TODO: test the import function with a more complex peopledb (uncomment the code)
        # TODO: factor out this pickle file creation (don't put it in setUp)
        test_peopledb = PeopleDatabase()
        test_peopledb.add_person_raw("Dunn, WL", 2)
        #test_peopledb.add_person_raw("Dunn, William", 4)
        #test_peopledb.add_person_raw("TEAGUE CE JR", 3)
        #test_peopledb.add_person_raw("TEMKO SL, COVINGTON AND BURLING", 1)
        test_peopledb.merge_duplicates()
        print("created test people db:")
        print(test_peopledb)
        self.test_peopledb_pickle = Path(DATA_PATH, 'django', 'test_peopledb.pickle')
        test_peopledb.store_to_disk(self.test_peopledb_pickle)
        # TODO: write test for importing docs csv
        # self.test_docs_csv =

    def test_is_this_on(self):
        """ Trivial test to make sure the testing system is working """
        self.assertTrue(2+2 == 4)

    def test_import_peopledb_to_person_model(self):
        import_peopledb_to_person_model(self.test_peopledb_pickle)
        print("imported django database:")
        print(DjangoPerson.objects.all())
        # TODO: implement aliases as a Counter in name_disambiguation
        DjangoPerson.objects.get(last="DUNN",
                         first="W",
                         middle="L",
                         most_likely_org="not calculated",
                         positions=json.dumps(Counter()),
                         aliases=json.dumps(Counter({"DUNN, WL": 2})),
                         count=2
                         )


