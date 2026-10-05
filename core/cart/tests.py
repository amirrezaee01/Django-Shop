from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError, transaction

from accounts.models import User
from cart.models import CartItemModel, CartModel
from shop.models import ProductModel, ProductStatusType


class CartFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "cart@example.com", password="a-long-test-password", is_verified=True
        )
        cls.product = ProductModel.objects.create(
            user=cls.user,
            title="Cart product",
            slug="cart-product",
            description="test",
            stock=5,
            price=1000,
            status=ProductStatusType.publish,
        )

    def test_verified_user_can_log_in(self):
        self.assertTrue(
            self.client.login(
                email="cart@example.com", password="a-long-test-password"
            )
        )

    def test_session_cart_adds_and_persists_product(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("cart:session-add-product"),
            {"product_id": str(self.product.pk), "quantity": "2"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        item = CartItemModel.objects.get(product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_invalid_product_id_returns_validation_response(self):
        response = self.client.post(
            reverse("cart:session-add-product"),
            {"product_id": "not-a-number", "quantity": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["code"], "invalid_product")

    def test_quantity_cannot_be_added_for_out_of_stock_product(self):
        self.product.stock = 0
        self.product.save(update_fields=["stock"])
        self.client.post(
            reverse("cart:session-add-product"),
            {"product_id": str(self.product.pk), "quantity": "1"},
        )
        response = self.client.post(
            reverse("cart:session-update-product-quantity"),
            {"product_id": str(self.product.pk), "quantity": "1"},
        )

        self.assertFalse(response.json()["success"])
        self.assertFalse(CartItemModel.objects.exists())

    def test_cart_constraints_reject_duplicate_cart_and_product_rows(self):
        cart = CartModel.objects.create(user=self.user)
        CartItemModel.objects.create(cart=cart, product=self.product, quantity=1)

        with self.assertRaises(IntegrityError), transaction.atomic():
            CartModel.objects.create(user=self.user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            CartItemModel.objects.create(cart=cart, product=self.product, quantity=2)
