"""
Tests for the main app.
"""
import django
import json
from django.test import TestCase
from collections import Counter
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from .serializers import PersonInfoSerializer
from .models import Person
from .views import get_person_info
import os
from pathlib import Path
from name_disambiguation.people_db import PeopleDatabase
from name_disambiguation.config import DATA_PATH
from apps.main.models import DjangoPerson
from apps.main.models import Document
from apps.main.models import import_peopledb_to_person_model
from apps.main.models import import_csv_to_document_model
os.environ.setdefault("DJANGO_SETTINGS_MODULE", __file__)
django.setup()


class MainTests(TestCase):
    def setUp(self):
        Person.objects.create(
            last="LAB",
            first="MIT",
            middle="DH",
            full_name="MIT DH LAB",
            most_likely_org="MIT YAY",
            positions=json.dumps(Counter()),
            aliases=json.dumps(Counter()),
            count=5)
        Person.objects.create(
            last="LAR",
            first="MOT",
            middle="DJ",
            full_name="MOT DJ LAR",
            most_likely_org="KIT BAY",
            positions=json.dumps(Counter()),
            aliases=json.dumps(Counter()),
            count=3)
        Person.objects.create(
            last="BOBBERT",
            first="BOB",
            middle="BOBSON",
            full_name="BOB BOBSON BOBBERT",
            most_likely_org="MIT",
            positions=json.dumps(Counter()),
            aliases=json.dumps(Counter()),
            count=5)
        self.factory = APIRequestFactory()

    def test_models_01(self):
        dummy_1 = Person.objects.get(last='LAB')
        dummy_2 = Person.objects.get(last='LAR')
        s = f'{dummy_1.first} {dummy_1.middle} {dummy_1.last}'
        s = s + ", Position: " + str(dummy_1.positions) + ", Aliases: " + \
            str(dummy_1.aliases) + ", count: " + str(dummy_1.count)

        s2 = f'{dummy_2.first} {dummy_2.middle} {dummy_2.last}'
        s2 = s2 + ", Position: " + str(dummy_2.positions) + ", Aliases: " + \
            str(dummy_2.aliases) + ", count: " + str(dummy_2.count)
        self.assertEqual(
            str(dummy_1), s)
        self.assertEqual(
            str(dummy_2), s2)

    def test_api_views_01(self):
        """tests that get_person_info returns correct person info when the person is in the
        database"""
        self.factory = APIRequestFactory()
        request = self.factory.get('/api/person_info/', {'full_name': 'BOB BOBSON BOBBERT'})
        dummy_1 = Person.objects.filter(full_name='BOB BOBSON BOBBERT')
        serializer = PersonInfoSerializer(instance=dummy_1, many=True)
        expected = Response(serializer.data)
        result = get_person_info(request)
        self.assertEqual(expected.data, result.data)

    def test_api_views_02(self):
        """tests that get_person_info returns correct person info when the person is NOT in the
        database"""
        Person.objects.create(
            last="",
            first="",
            middle="",
            full_name="JANE DOE DEERE not available.",
            most_likely_org="",
            positions=json.dumps(Counter()),
            aliases=json.dumps(Counter()),
            count=0)
        request = self.factory.get('/api/person_info/', {'full_name': 'JANE DOE DEERE'})
        dummy_1 = Person.objects.get(full_name='JANE DOE DEERE not available.')
        serializer = PersonInfoSerializer(instance=dummy_1, many=False)
        expected = Response(serializer.data)
        result = get_person_info(request)
        self.assertEqual(expected.data, result.data)




class ModelsTests(TestCase):
    """
    Tests import methods in models.py
    """
    def setUp(self):
        # create a small PeopleDatabase for testing
        test_peopledb = PeopleDatabase()
        test_peopledb.add_person_raw("Dunn, WL", 2)
        test_peopledb.add_person_raw("Dunn, William L", 4)
        test_peopledb.add_person_raw("TEAGUE CE JR", 3)
        test_peopledb.add_person_raw("TEMKO SL, COVINGTON AND BURLING", 5)
        test_peopledb.add_person_raw("TEMKO SL, COVINGTON BURLING", 3)
        test_peopledb.add_person_raw("TEMKO SL, COVINGTON BURLING", 3)
        # merge duplicate people
        test_peopledb.merge_duplicates(print_merge_results_for_name=None)
        # store it as a picke file
        self.test_peopledb_pickle = Path(DATA_PATH, 'django', 'test_peopledb.pickle')
        test_peopledb.store_to_disk(self.test_peopledb_pickle)
        # file path to test csv file for docs
        self.test_docs_csv = Path(DATA_PATH, "django", "test_import_docs.csv")

    def test_import_peopledb_to_person(self):
        """
        Tests import_peopledb_to_person_model() in models.py
        imports peopledb from test pickle file & create corresponding DjangoPerson database
        :return:
        """
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

    def test_import_csv_to_document(self):
        """
        Tests import_csv_to_document_model() in models.py
        :return:
        """
        # First create DjangoPerson database from the test pickle file
        import_peopledb_to_person_model(self.test_peopledb_pickle)
        # Then create Document database from the test csv file
        import_csv_to_document_model(self.test_docs_csv)
        # Test if the correct Document objects are stored
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
        # Test if the authors & recipients ManyToManyField are stored correctly
        self.assertEqual(len(Document.objects.filter(authors__last="DUNN").all()), 2)
        self.assertEqual(len(Document.objects.filter(authors__full_name="C E TEAGUE").all()), 1)
        self.assertEqual(len(Document.objects.filter(authors__full_name="S L TEMKO").all()), 0)

        self.assertEqual(len(Document.objects.filter(recipients__last="DUNN").all()), 0)
        self.assertEqual(len(Document.objects.filter(recipients__last="TEAGUE").all()), 1)
        self.assertEqual(len(Document.objects.filter(recipients__last="TEMKO").all()), 1)

    def test_import_csv_to_document_2(self):
        """
        Tests import_csv_to_document_model() in models.py:
        Tests when the authors/recipients do not exist in the current DjangoPerson database,
        the correct DjangoPerson objects are created & the authors/recipients are stored correctly
        :return:
        """
        import_csv_to_document_model(self.test_docs_csv)
        self.assertEqual(len(Document.objects.filter(authors__last="DUNN").all()), 2)
        self.assertEqual(len(Document.objects.filter(authors__full_name="C E TEAGUE").all()), 1)
        self.assertEqual(len(Document.objects.filter(authors__full_name="S L TEMKO").all()), 0)
        self.assertEqual(len(Document.objects.filter(recipients__last="DUNN").all()), 0)
        self.assertEqual(len(Document.objects.filter(recipients__last="TEAGUE").all()), 1)
        self.assertEqual(len(Document.objects.filter(recipients__last="TEMKO").all()), 1)

        DjangoPerson.objects.get(last="DUNN", first="W", middle="L",
                                 full_name="W L DUNN",
                                 most_likely_org="not calculated",
                                 positions=json.dumps(Counter()),
                                 aliases=json.dumps(Counter(["DUNN, WL"])),
                                 count=1
                                 )
        DjangoPerson.objects.get(last="TEAGUE", first="C", middle="E",
                                 full_name="C E TEAGUE",
                                 most_likely_org="not calculated",
                                 positions=json.dumps(Counter(["JR"])),
                                 aliases=json.dumps(Counter(["TEAGUE CE JR"])),
                                 count=1
                                 )
        DjangoPerson.objects.get(last="TEMKO", first="S", middle="L",
                                 full_name="S L TEMKO",
                                 most_likely_org="not calculated",
                                 positions=json.dumps(Counter()),
                                 aliases=json.dumps(Counter(["TEMKO SL"])),
                                 count=1
                                 )
