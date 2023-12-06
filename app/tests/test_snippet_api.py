# -*- coding: utf-8 -*-
"""
File: test_snippet_api.py
Authors: Veaceslav Kunitki<tumikosha@fmail.com>
Description: tests for snippet APi
"""

from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from app.models import Snippet
from django.urls import reverse


ENDPOINT_FOR_SNIPPET = reverse('app:snippet-list-create')


class SnippetAPITestCase(APITestCase):
    """Test if logged users have access to API endpoint"""

    def setUp(self):
        # Create some test data
        self.my_model_data = {'code': '2+2'}
        Snippet.objects.create(**self.my_model_data)
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_create_Snippet(self):
        # Test creating an object
        response = self.client.post(ENDPOINT_FOR_SNIPPET, data=self.my_model_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Snippet.objects.count(), 2)  # Assuming we started with one object

    def test_list_Snippet(self):
        # Test listing objects
        response = self.client.get(ENDPOINT_FOR_SNIPPET)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), 1)  # Assuming you only have one object in the database
        # assert len(response.data) > 0  # Assuming we have snippets in the database

    def test_create_and_list__Snippet(self):
        # create object

        response = self.client.post(ENDPOINT_FOR_SNIPPET, data={'code': '1+1'}, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        response = self.client.post(ENDPOINT_FOR_SNIPPET, data={'code': '2+2'}, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        response = self.client.get(ENDPOINT_FOR_SNIPPET)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        first_snippet: Snippet = response.data[0]
        second_snippet: Snippet = response.data[1]
        assert first_snippet['author'] == 1
        assert second_snippet['author'] == 1
        assert second_snippet['code'] == "1+1"
        assert first_snippet['code'] == "2+2"

        # self.assertEqual(len(response.data), 1)  # Assuming you only have one object in the database
        assert len(response.data) > 0  # Assuming we have snippets in the database


class SnippetAPIWithoutLoginTestCase(APITestCase):
    """ SecurityTest: Not logged users should not have  access to API ENDPOINT """

    def setUp(self):
        # Create some test data
        self.my_model_data = {'code': '2+2'}

    def test_create_Snippet(self):
        # Test creating an object
        response = self.client.post(ENDPOINT_FOR_SNIPPET, data=self.my_model_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_Snippet(self):
        # Test listing objects
        response = self.client.get(ENDPOINT_FOR_SNIPPET)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert len(response.data) > 0  # Assuming we have snippets in the database


