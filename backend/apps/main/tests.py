"""
Tests for the main app.
"""

from django.test import TestCase
import json
from pathlib import Path
from collections import Counter
from name_disambiguation.people_db import PeopleDatabase
from name_disambiguation.name_preprocessing import parse_column_person
from name_disambiguation.config import DATA_PATH
from apps.main.models import DjangoPerson
from apps.main.models import Document
from apps.main.models import import_peopledb_to_person_model
from apps.main.models import import_csv_to_document_model

class MainTests(TestCase):
    def setUp(self):
        # create a small PeopleDatabase for testing
        test_peopledb = PeopleDatabase()
        test_peopledb.add_person_raw("Dunn, WL", 2)
        test_peopledb.add_person_raw("Dunn, William L", 4)
        test_peopledb.add_person_raw("TEAGUE CE JR", 3)
        test_peopledb.add_person_raw("TEMKO SL, COVINGTON AND BURLING", 5)
        test_peopledb.add_person_raw("TEMKO SL, COVINGTON BURLING", 3)
        # merge duplicate people
        test_peopledb.merge_duplicates(print_merge_results_for_name=None)
        # store it as a picke file
        self.test_peopledb_pickle = Path(DATA_PATH, 'django', 'test_peopledb.pickle')
        test_peopledb.store_to_disk(self.test_peopledb_pickle)
        # file path to test csv file for docs
        self.test_docs_csv = Path(DATA_PATH, "django", "test_import_docs.csv")

    def test_import_peopledb_to_person_model(self):
        # tests import_peopledb_to_person_model() in models.py
        # imports peopledb from test pickle file & create corresponding DjangoPerson database
        import_peopledb_to_person_model(self.test_peopledb_pickle)

        # tests if the correct DjangoPerson objects are stored (by searching for them)
        # TODO: (maybe want to fix this) since aliases is a string, the order matters when you
        #  try to compare aliases Counters -- should we alphabetize when we json.dumps?
        DjangoPerson.objects.get(last="DUNN", first="WILLIAM", middle="L",
                                 full_name="WILLIAM L DUNN",
                                 most_likely_org="not calculated",
                                 positions=json.dumps(Counter()),
                                 aliases=json.dumps(Counter({"DUNN, WILLIAM L": 4, "DUNN, WL": 2})),
                                 count=6
                                 )
        DjangoPerson.objects.get(last="TEAGUE", first="C", middle="E",
                                 full_name="C E TEAGUE",
                                 most_likely_org="not calculated",
                                 positions=json.dumps(Counter({"JR": 3})),
                                 aliases=json.dumps(Counter({"TEAGUE CE JR": 3})),
                                 count=3
                                 )
        DjangoPerson.objects.get(last="TEMKO", first="S", middle="L",
                                 full_name="S L TEMKO",
                                 most_likely_org="not calculated",
                                 positions=json.dumps(Counter({"COVINGTON & BURLING": 8})),
                                 aliases=json.dumps(Counter({
                                     "TEMKO SL, COVINGTON AND BURLING": 5,
                                     "TEMKO SL, COVINGTON BURLING": 3
                                 })),
                                 count=8
                                 )

    def test_import_csv_to_document_model(self):
        import_peopledb_to_person_model(self.test_peopledb_pickle)
        import_csv_to_document_model(self.test_docs_csv)
        print(Document.objects.all())
        Document.objects.get(au="TEMKO SL",
                             au_org="",
                             au_person="Dunn, WL; TEAGUE CE JR",
                             cc="TEMKO SL",
                             cc_org="COVINGTON BURLING",
                             collection="collection1",
                             date="2019-11-15",
                             doc_type="letter",
                             pages=10,
                             rc="TEAGUE CE JR",
                             rc_org="",
                             rc_person="",
                             text="hi teague how's it going",
                             tid="0x12sss",
                             title="letter1"
                             )
        self.assertEqual(len(Document.objects.filter(authors__last="DUNN").all()), 2)
        self.assertEqual(len(Document.objects.filter(authors__full_name="C E TEAGUE").all()), 1)
        self.assertEqual(len(Document.objects.filter(authors__full_name="S L TEMKO").all()), 0)

        self.assertEqual(len(Document.objects.filter(recipients__last="DUNN").all()), 0)
        self.assertEqual(len(Document.objects.filter(recipients__last="TEAGUE").all()), 1)
        self.assertEqual(len(Document.objects.filter(recipients__last="TEMKO").all()), 1)


