from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from tasks.models import Task
from django.contrib.auth import get_user_model



class CustomTokenObtainPairViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            phone_number='+1234567890',
            email='test@example.com',
            password='password123'
        )

    def test_token_obtain(self):
        url = reverse('token_obtain_pair')
        data = {
            'phone_number': '+1234567890',
            'password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)