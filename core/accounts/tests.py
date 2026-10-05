from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class AuthenticationFlowTests(TestCase):
    def test_verified_user_can_log_in(self):
        User.objects.create_user(
            "login@example.com", password="a-long-test-password", is_verified=True
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "login@example.com", "password": "a-long-test-password"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_unverified_user_cannot_log_in(self):
        User.objects.create_user(
            "unverified@example.com",
            password="a-long-test-password",
            is_verified=False,
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "unverified@example.com", "password": "a-long-test-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "حساب شما فعال نشده است")
