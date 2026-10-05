import json
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, TestCase, override_settings

from payment.zarinpal_client import (
    PaymentConfigurationError,
    PaymentGatewayError,
    ZarinPalSandbox,
)
from payment.models import PaymentModel, PaymentStatusType
from order.models import OrderModel, OrderStatusType
from accounts.models import User


class ZarinPalClientTests(SimpleTestCase):
    @override_settings(MERCHANT_ID="")
    def test_missing_merchant_id_is_a_configuration_error(self):
        with self.assertRaisesMessage(PaymentConfigurationError, "MERCHANT_ID"):
            ZarinPalSandbox()

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.zarinpal_client.requests.post")
    def test_authority_is_required_before_checkout_continues(self, post):
        gateway_response = Mock()
        gateway_response.json.return_value = {"Status": -9, "Errors": "invalid merchant"}
        post.return_value = gateway_response

        with self.assertRaises(PaymentGatewayError):
            ZarinPalSandbox().payment_request(
                1000, callback_url="https://shop.test/payment/verify/"
            )

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.zarinpal_client.requests.post")
    def test_success_status_without_authority_is_rejected(self, post):
        gateway_response = Mock()
        gateway_response.json.return_value = {"Status": 100}
        post.return_value = gateway_response

        with self.assertRaisesMessage(PaymentGatewayError, "no payment authority"):
            ZarinPalSandbox().payment_request(
                1000, callback_url="https://shop.test/payment/verify/"
            )

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.zarinpal_client.requests.post")
    def test_successful_payment_request_keeps_authority(self, post):
        gateway_response = Mock()
        gateway_response.json.return_value = {"Status": 100, "Authority": "A123"}
        post.return_value = gateway_response

        result = ZarinPalSandbox().payment_request(
            1000, callback_url="https://shop.test/payment/verify/"
        )

        self.assertEqual(result["Authority"], "A123")
        self.assertEqual(post.call_args.kwargs["timeout"], (5, 20))
        self.assertEqual(
            json.loads(post.call_args.kwargs["data"])["CallbackURL"],
            "https://shop.test/payment/verify/",
        )

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.zarinpal_client.requests.post")
    def test_verification_network_failure_is_reported_safely(self, post):
        import requests

        post.side_effect = requests.Timeout("timeout")

        with self.assertRaisesMessage(PaymentGatewayError, "could not verify"):
            ZarinPalSandbox().payment_verify(1000, "A123")

        self.assertEqual(post.call_args.kwargs["timeout"], (5, 20))

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.zarinpal_client.requests.post")
    def test_successful_verification_requires_a_numeric_reference_id(self, post):
        gateway_response = Mock()
        gateway_response.json.return_value = {"Status": 100, "RefID": "invalid"}
        post.return_value = gateway_response

        with self.assertRaisesMessage(PaymentGatewayError, "invalid verification response"):
            ZarinPalSandbox().payment_verify(1000, "A123")


class PaymentVerificationViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("payment@example.com", password="test-password")
        self.payment = PaymentModel.objects.create(authority_id="A123", amount=1000)
        self.order = OrderModel.objects.create(
            user=user,
            address="Test address",
            state="State",
            city="City",
            zip_code="00000",
            payment=self.payment,
        )

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.views.ZarinPalSandbox")
    def test_successful_verification_updates_payment_and_order(self, gateway_class):
        gateway_class.return_value.payment_verify.return_value = {
            "Status": 100,
            "RefID": 123456,
        }

        response = self.client.get(
            "/payment/verify/", {"Authority": "A123", "Status": "OK"}
        )

        self.assertRedirects(response, "/order/completed/", fetch_redirect_response=False)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.payment.status, PaymentStatusType.success)
        self.assertEqual(self.payment.ref_id, 123456)
        self.assertEqual(self.order.status, OrderStatusType.success)

    @override_settings(MERCHANT_ID="sandbox-merchant")
    @patch("payment.views.ZarinPalSandbox")
    def test_provider_unavailable_leaves_pending_records_unchanged(self, gateway_class):
        gateway_class.return_value.payment_verify.side_effect = PaymentGatewayError("offline")

        response = self.client.get(
            "/payment/verify/", {"Authority": "A123", "Status": "OK"}
        )

        self.assertEqual(response.status_code, 503)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.payment.status, PaymentStatusType.pending)
        self.assertEqual(self.order.status, OrderStatusType.pending)
