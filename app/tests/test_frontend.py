# -*- coding: utf-8 -*-
"""
File: test_frontend.py
Authors: Veaceslav Kunitki<tumikosha@fmail.com>
Description: tests for FrontEnd & robots.txt
"""

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User


class FrontendRobotStaticFilesTestCase(APITestCase):
    """ This class has tests for static files serving & robots.txt """

    def setUp(self):
        self.user = User.objects.create_user('username', 'Pas$w0rd')

    def test_robots_txt(self):
        """ Just test if first page opens"""
        response = self.client.get(reverse('app:robots'))
        assert response.status_code == 200

    def test_app_static_folder(self):
        """ Just test ifstatic files loads"""
        response = self.client.get('/static/app/static_file_example.txt')
        assert response.status_code == 200

    def test_homepage(self):
        """ Just test if first page opens"""
        response = self.client.get(reverse('app:index'))
        assert response.status_code == 200

    def test_homepage_without_login(self):
        """ Just test if first page opens without login and show info about it"""
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, f"You are not logged in")
        assert response.status_code == 200

    def test_homepage_after_login(self):
        """ Just test if first page opens after login and welcome username"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, f"{self.user.username}")
        assert response.status_code == 200
