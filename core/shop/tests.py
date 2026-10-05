from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from accounts.models import User
from .models import ProductModel, ProductStatusType, WishlistProductModel


class ShopViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("seller@example.com", password="a-long-test-password")
        cls.product = ProductModel.objects.create(
            user=user,
            title="Published item",
            slug="published-item",
            description="A test product",
            price=1000,
            status=ProductStatusType.publish,
        )
        ProductModel.objects.create(
            user=user,
            title="Draft item",
            slug="draft-item",
            description="Hidden from the shop",
            price=500,
            status=ProductStatusType.draft,
        )
        for index in range(10):
            ProductModel.objects.create(
                user=user,
                title=f"Other item {index}",
                slug=f"other-item-{index}",
                description="Another test product",
                price=1100,
                status=ProductStatusType.publish,
            )

    def test_listing_hides_drafts_and_applies_filters(self):
        response = self.client.get(reverse("shop:product-grid"), {"q": "Published", "min_price": "900"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item.pk for item in response.context["object_list"]], [self.product.pk])

    def test_invalid_filter_and_page_size_do_not_crash(self):
        response = self.client.get(reverse("shop:product-grid"), {"min_price": "not-a-price", "page_size": "many"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["paginator"].count, 0)

    def test_listing_is_paginated(self):
        response = self.client.get(reverse("shop:product-grid"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["object_list"]), 2)

    def test_product_price_calculation(self):
        self.product.discount_percent = 25
        self.assertEqual(self.product.get_price(), 750)

    def test_wishlist_rejects_duplicate_product_for_user(self):
        customer = User.objects.create_user("customer@example.com", password="a-long-test-password")
        WishlistProductModel.objects.create(user=customer, product=self.product)
        with self.assertRaises(IntegrityError):
            WishlistProductModel.objects.create(user=customer, product=self.product)

    def test_product_detail_is_public(self):
        response = self.client.get(reverse("shop:product-detail", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)

    def test_wishlist_toggle_adds_and_removes_product(self):
        customer = User.objects.create_user("wishlist@example.com", password="a-long-test-password")
        self.client.force_login(customer)
        url = reverse("shop:add-or-remove-wishlist")

        added = self.client.post(url, {"product_id": self.product.pk})
        self.assertEqual(added.status_code, 200)
        self.assertTrue(WishlistProductModel.objects.filter(user=customer, product=self.product).exists())

        removed = self.client.post(url, {"product_id": self.product.pk})
        self.assertEqual(removed.status_code, 200)
        self.assertFalse(WishlistProductModel.objects.filter(user=customer, product=self.product).exists())

    def test_wishlist_toggle_requires_authentication(self):
        response = self.client.post(
            reverse("shop:add-or-remove-wishlist"), {"product_id": self.product.pk}
        )

        self.assertEqual(response.status_code, 302)
