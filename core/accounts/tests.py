from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserType


class AuthenticationFlowTests(TestCase):
    def test_dashboard_home_redirects_customer_on_get(self):
        user = User.objects.create_user(
            "dashboard@example.com", password="a-long-test-password",
            type=UserType.customer.value,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:customer:home"))

    def test_dashboard_home_redirects_admin_user_on_get(self):
        user = User.objects.create_user(
            "admin-dashboard@example.com", password="a-long-test-password",
            type=UserType.admin.value,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:admin:home"))
        dashboard_response = self.client.get(response.url)
        self.assertEqual(dashboard_response.status_code, 200)

    def test_dashboard_home_redirects_django_superuser_to_admin_dashboard(self):
        user = User.objects.create_superuser(
            "superuser-dashboard@example.com", password="a-long-test-password"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:admin:home"))
        dashboard_response = self.client.get(response.url)
        self.assertEqual(dashboard_response.status_code, 200)

    def test_dashboard_home_routes_staff_user_to_admin_dashboard(self):
        user = User.objects.create_user(
            "staff-dashboard@example.com", password="a-long-test-password",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:admin:home"))
        self.assertEqual(self.client.get(response.url).status_code, 200)

    def test_customer_cannot_open_admin_dashboard(self):
        user = User.objects.create_user(
            "customer-dashboard@example.com", password="a-long-test-password",
            type=UserType.customer.value,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:admin:home"))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_home_requires_authentication(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("accounts:login"))

    def test_logout_requires_post_and_clears_session(self):
        user = User.objects.create_user("logout@example.com", password="password")
        self.client.force_login(user)

        get_response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(get_response.status_code, 405)
        self.assertTrue("_auth_user_id" in self.client.session)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, "/")
        self.assertFalse("_auth_user_id" in self.client.session)

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
