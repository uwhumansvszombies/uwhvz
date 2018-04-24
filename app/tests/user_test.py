from django.test import TestCase

from app.models import User


class UserCreationTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(email='test@email.com', password='hunter2')
        self.assertEqual(user.email, 'test@email.com')
