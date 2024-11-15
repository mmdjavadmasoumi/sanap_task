from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from tasks.models import Task

class TaskTests(APITestCase):

    def setUp(self):
        # Create instructor and client users
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="password123",
            phone_number="+1234567890",
            user_type=1,  # Instructor
        )
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="password123",
            phone_number="+0987654321",
            user_type=2,  # Client
        )

        # Create test tasks
        self.task1 = Task.objects.create(title="Task 1", status="pending", user=self.instructor)
        self.task2 = Task.objects.create(title="Task 2", status="completed", user=self.instructor)

        # Get JWT tokens for both instructor and client
        self.instructor_token = self.get_jwt_token(self.instructor.phone_number, 'password123')
        self.client_token = self.get_jwt_token(self.client_user.phone_number, 'password123')

    def get_jwt_token(self, phone_number, password):
        """Helper method to get JWT token for a user."""
        url = reverse('token_obtain_pair')  # Endpoint for JWT token
        data = {
            'phone_number': phone_number,
            'password': password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']  # Return the access token

    def test_task_list_view_as_instructor(self):
        """Test that an instructor can view the task list."""
        url = reverse('task-list-create')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assert there are 2 tasks

    def test_task_list_view_as_client(self):
        """Test that a client can view the task list."""
        url = reverse('task-list-create')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0, "Response data should contain tasks for the instructor")

    def test_create_task_as_instructor(self):
        """Test that an instructor can create a new task."""
        url = reverse('task-list-create')
        data = {"title": "New Task", "status": "in_progress"}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Task")

    def test_create_task_as_client(self):
        """Test that a client cannot create a new task."""
        url = reverse('task-list-create')
        data = {"title": "New Task", "status": "in_progress"}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_task_detail_view(self):
        """Test that a user can view task details."""
        url = reverse('task-detail', kwargs={'pk': self.task1.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.task1.title)

    def test_update_task(self):
        """Test that an instructor can update a task."""
        url = reverse('task-detail', kwargs={'pk': self.task1.id})
        data = {"title": "Updated Task 1"}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Task 1")

    def test_delete_task(self):
        """Test that an instructor can delete a task."""
        url = reverse('task-detail', kwargs={'pk': self.task1.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
