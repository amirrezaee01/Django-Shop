from django.views.generic import ListView, DetailView, View
from .models import ProductModel, ProductStatusType, ProductCategoryModel, WishlistProductModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Count, Q
from decimal import Decimal, InvalidOperation
from review.models import ReviewModel, ReviewStatusType
# Create your views here.
# Create your views here.


class ShopProductGridView(ListView):
    template_name = "shop/product_grid.html"
    paginate_by = 9

    def get_paginate_by(self, queryset):
        try:
            return min(max(int(self.request.GET.get("page_size", self.paginate_by)), 1), 36)
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self):
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value).prefetch_related("category")
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category_id"):
            try:
                queryset = queryset.filter(category__id=int(category_id))
            except (TypeError, ValueError):
                return queryset.none()
        try:
            if (min_price := self.request.GET.get("min_price")) not in (None, ""):
                min_value = Decimal(min_price)
                if not min_value.is_finite():
                    return queryset.none()
                queryset = queryset.filter(price__gte=min_value)
            if (max_price := self.request.GET.get("max_price")) not in (None, ""):
                max_value = Decimal(max_price)
                if not max_value.is_finite():
                    return queryset.none()
                queryset = queryset.filter(price__lte=max_value)
        except InvalidOperation:
            return queryset.none()
        if order_by := self.request.GET.get("order_by"):
            allowed_ordering = {"price", "-price", "created_date", "-created_date", "title", "-title"}
            if order_by in allowed_ordering:
                queryset = queryset.order_by(order_by, "pk")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ Count only once instead of calling get_queryset() again
        context["total_items"] = context["page_obj"].paginator.count

        # ✅ Only query wishlist if user is authenticated
        if self.request.user.is_authenticated:
            context["wishlist_items"] = list(
                WishlistProductModel.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
        else:
            context["wishlist_items"] = []  # ✅ Empty list for guest users

        # ✅ Prevent duplicate categories using distinct()
        context["categories"] = ProductCategoryModel.objects.filter(
            productmodel__status=ProductStatusType.publish.value
        ).distinct()

        return context


class ShopProductDetailView(DetailView):
    template_name = "shop/product-detail.html"
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value
    ).prefetch_related("product_images", "category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context["is_wished"] = WishlistProductModel.objects.filter(
            user=self.request.user, product__id=product.id).exists() if self.request.user.is_authenticated else False
        reviews = ReviewModel.objects.filter(
            product=product, status=ReviewStatusType.accepted.value
        ).select_related("user", "user__user_profile")
        context["reviews"] = reviews
        stats = reviews.aggregate(
            total=Count("pk"),
            **{f"rate_{rate}": Count("pk", filter=Q(rate=rate)) for rate in range(1, 6)},
        )
        total_reviews_count = stats["total"]
        context["reviews_count"] = {
            f"rate_{rate}": stats[f"rate_{rate}"] for rate in range(1, 6)
        }
        if total_reviews_count != 0:
            context["reviews_avg"] = {
                f"rate_{rate}": round((stats[f"rate_{rate}"] / total_reviews_count) * 100, 2) for rate in range(1, 6)
            }
        else:
            context["reviews_avg"] = {f"rate_{rate}": 0 for rate in range(1, 6)}
        return context

class AddOrRemoveWishlistView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        message = ""
        if product_id:
            try:
                product_id = int(product_id)
            except (TypeError, ValueError):
                return JsonResponse({"message": "شناسه محصول نامعتبر است"}, status=400)
            if not ProductModel.objects.filter(pk=product_id).exists():
                return JsonResponse({"message": "محصول یافت نشد"}, status=404)
            try:
                wishlist_item = WishlistProductModel.objects.get(user=request.user, product_id=product_id)
                wishlist_item.delete()
                message = "محصول از لیست علایق حذف شد"
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id
                )
                message = "محصول به لیست علایق اضافه شد"

        return JsonResponse({"message": message})
