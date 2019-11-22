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
