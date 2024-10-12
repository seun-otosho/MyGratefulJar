import unittest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.User = get_user_model()

    def tearDown(self):
        self.User.objects.all().delete()

    def test_valid_user_creation(self):
        user = self.User.objects.create(username='test-username', email='test@example.com')
        self.assertIsInstance(user, self.User)
        self.assertEqual(user.username, 'test-username')
        self.assertEqual(user.email, 'test@example.com')

    def test_username_uniqueness(self):
        self.User.objects.create(username='duplicate-username', email='test1@example.com')
        with self.assertRaises(IntegrityError):
            self.User.objects.create(username='duplicate-username', email='test2@example.com')

    def test_email_uniqueness(self):
        self.User.objects.create(username='username-1', email='duplicate-email@example.com')
        with self.assertRaises(IntegrityError):
            self.User.objects.create(username='username-2', email='duplicate-email@example.com')

    def test_username_enforces_regex(self):
        user = self.User(username='invalid*username', email='test@example.com')
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_has_perm_returns_true(self):
        user = self.User.objects.create(username='test-username', email='test@example.com')
        self.assertTrue(user.has_perm('any perm'))

    def test_has_module_perms_returns_true(self):
        user = self.User.objects.create(username='test-username', email='test@example.com')
        self.assertTrue(user.has_module_perms('any app_label'))


if __name__ == "__main__":
    unittest.main()
