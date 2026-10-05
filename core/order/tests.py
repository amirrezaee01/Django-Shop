from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from unittest.mock import Mock, patch

from accounts.models import User
from cart.models import CartItemModel, CartModel
from core.query_utils import filter_partial_id
from order.models import CouponModel, OrderModel, UserAddressModel
from payment.models import PaymentModel
from payment.zarinpal_client import PaymentGatewayError
from shop.models import ProductModel, ProductStatusType


class PartialOrderIdSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("orders@example.com", password="a-long-test-password")
        cls.orders = [
            OrderModel.objects.create(
                user=user,
                address="Test address",
                state="State",
                city="City",
                zip_code="00000",
            )
            for _ in range(12)
        ]

    def test_partial_search_matches_order_ids(self):
        expected = [order.pk for order in self.orders if "1" in str(order.pk)]
        results = filter_partial_id(OrderModel.objects.all(), "1").order_by("pk")
        self.assertEqual(list(results.values_list("pk", flat=True)), expected)

    def test_coupon_price_uses_decimal_percentage(self):
        coupon = CouponModel.objects.create(code="TEN", discount_percent=15)
        order = self.orders[0]
        order.coupon = coupon
        order.total_price = 1000

        self.assertEqual(order.get_price(), 850)


class CheckoutPaymentFailureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("checkout@example.com", password="a-long-test-password")
        cls.address = UserAddressModel.objects.create(
            user=cls.user,
            address="Test address",
            state="State",
            city="City",
            zip_code="00000",
        )
        product = ProductModel.objects.create(
            user=cls.user,
            title="Checkout product",
            slug="checkout-product",
            description="test",
            price=1000,
            status=ProductStatusType.publish,
        )
        cart = CartModel.objects.create(user=cls.user)
        CartItemModel.objects.create(cart=cart, product=product, quantity=1)

    def post_checkout(self):
        self.client.force_login(self.user)
        return self.client.post(
            reverse("order:checkout"),
            {"address_id": self.address.pk, "coupon": ""},
        )

    @override_settings(MERCHANT_ID="")
    def test_missing_merchant_id_is_reported_without_clearing_cart(self):
        response = self.post_checkout()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MERCHANT_ID")
        self.assertEqual(OrderModel.objects.count(), 0)
        self.assertEqual(CartItemModel.objects.count(), 1)

    @override_settings(MERCHANT_ID="configured-merchant")
    @patch("order.views.ZarinPalSandbox")
    def test_gateway_failure_rolls_back_order_and_preserves_cart(self, gateway_class):
        gateway_class.return_value.payment_request.side_effect = PaymentGatewayError(
            "gateway unavailable"
        )

        response = self.post_checkout()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gateway unavailable")
        self.assertEqual(OrderModel.objects.count(), 0)
        self.assertEqual(CartItemModel.objects.count(), 1)

    @override_settings(MERCHANT_ID="configured-merchant")
    @patch("order.views.ZarinPalSandbox")
    def test_successful_checkout_uses_real_callback_and_clears_cart(self, gateway_class):
        gateway = gateway_class.return_value
        gateway.payment_request.return_value = {"Status": 100, "Authority": "A123"}
        gateway.generate_payment_url.return_value = "https://sandbox.zarinpal.com/pg/StartPay/A123"

        response = self.post_checkout()

        self.assertRedirects(response, gateway.generate_payment_url.return_value, fetch_redirect_response=False)
        self.assertEqual(OrderModel.objects.count(), 1)
        self.assertEqual(PaymentModel.objects.count(), 1)
        self.assertFalse(CartItemModel.objects.exists())
        self.assertEqual(
            gateway.payment_request.call_args.kwargs["callback_url"],
            "http://testserver/payment/verify/",
        )
