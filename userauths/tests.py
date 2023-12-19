from django.test import TestCase
from django.contrib import auth
# Create your tests here.
from rest_framework.test import APITestCase

class GoogleAuthTestCase(APITestCase):
    def test_google_authentication(self):
        # Simulate GET request to initiate Google authentication flow
        response = self.client.post('/accounts/google/login/')
        self.assertEqual(response.status_code, 302)  # Expecting redirection to Google authentication page

        # Simulate POST request to handle Google authentication callback
        response = self.client.get('/accounts/google/login/callback/')
        self.assertEqual(response.status_code, 200)  # Expecting successful callback handling
        # Add more assertions as needed to check data returned after successful authentication
