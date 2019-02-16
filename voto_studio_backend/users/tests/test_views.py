from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .. import models


class UsersAPITests(TestCase):
    def setUp(self):
        self.test_user = models.User.objects.create_user(
            'test@test.com',
            'John Doe',
            'testpass123',
        )
        self.create_url = reverse('users:register')

    def test_create_user(self):
        data = {
            'email': 'test2@test.com',
            'name': 'Jane Smith',
            'password': 'testtwopass123',
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(models.User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], data['email'])
        self.assertEqual(response.data['user']['name'], data['name'])
        self.assertFalse('password' in response.data)

        token = Token.objects.get(user=models.User.objects.latest('id'))
        self.assertEqual(response.data['user']['token'], token.key)

    def test_create_user_with_too_short_password(self):
        data = {
            'email': 'test3@test.com',
            'name': 'Jack Toby',
            'password': 'test',
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_too_long_name(self):
        data = {
            'email': 'test4@example.com',
            'name': 'Tom' * 30,
            'password': 'testfourpass123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(len(response.data['name']), 1)

    def test_create_user_with_too_short_name(self):
        data = {
            'email': 'test5@example.com',
            'name': 'T',
            'password': 'testpassfive123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(len(response.data['name']), 1)

    def test_create_user_with_preexisting_email(self):
        data = {
            'name': 'Jack Emil',
            'email': 'test@test.com',
            'password': 'testpasssix123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_invalid_email(self):
        data = {
            'name': 'Jack Emil',
            'email': 'test',
            'password': 'testpasssix123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_no_email(self):
        data = {
            'name': 'Jack Emil',
            'email': '',
            'password': 'testpasssix123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
