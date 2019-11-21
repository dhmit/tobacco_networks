"""
Tests for the main app.
"""
import json
from django.test import TestCase
from collections import Counter
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from .serializers import PersonInfoSerializer
from .models import Person
from .views import get_person_info
# from rest_framework.test import APIRequestFactory
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", __file__)
import django
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
        self.uri = '/api/'

    def test_is_this_on(self):
        """ Trivial test to make sure the testing system is working """
        self.assertTrue(2+2 == 4)

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

    # def test_api_views(self):
    #     Person.objects.create(
    #         last="LAB",
    #         first="MIT",
    #         middle="DH",
    #         full_name="MIT DH LAB",
    #         most_likely_org="MIT YAY",
    #         positions=json.dumps(Counter()),
    #         aliases=json.dumps(Counter()),
    #         count=5)
    #     self.factory = APIRequestFactory()
    #     dummy_1 = Person.objects.get(full_name='MIT DH LAB')
    #     dummy_1.save()
    #     serializer = PersonInfoSerializer(instance=dummy_1, many=False)
    #     expected = Response(serializer.data)
    #     request = self.factory.get(self.uri)
    #     result = get_person_info(request)
    #     self.assertEqual(expected, result)






