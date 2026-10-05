from django.views.generic import (
    View,
    TemplateView,
    UpdateView,
    ListView,
    DetailView,
    DeleteView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from django.contrib.auth import views as auth_views
from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from accounts.models import Profile
from django.shortcuts import redirect
from django.contrib import messages
from core.query_utils import apply_ordering, bounded_page_size
from decimal import Decimal, InvalidOperation
from ..forms import *

from shop.models import *


class AdminProductListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products/products-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return bounded_page_size(self.request, self.paginate_by)

    def get_queryset(self):
        queryset = ProductModel.objects.select_related("user").prefetch_related("category")
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category_id"):
            try:
                queryset = queryset.filter(category__id=int(category_id))
            except ValueError:
                return queryset.none()
        queryset = queryset.distinct()
        try:
            if (min_price := self.request.GET.get("min_price")) not in (None, ""):
                minimum = Decimal(min_price)
                if not minimum.is_finite():
                    return queryset.none()
                queryset = queryset.filter(price__gte=minimum)
            if (max_price := self.request.GET.get("max_price")) not in (None, ""):
                maximum = Decimal(max_price)
                if not maximum.is_finite():
                    return queryset.none()
                queryset = queryset.filter(price__lte=maximum)
        except InvalidOperation:
            return queryset.none()
        if order_by := self.request.GET.get("order_by"):
            queryset = apply_ordering(
                queryset, order_by, {"created_date", "title", "price", "stock", "status"}
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["page_obj"].paginator.count
        context["categories"] = ProductCategoryModel.objects.filter(
            productmodel__in=self.get_queryset()
        ).distinct()

        return context


class AdminProductCreateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView
):
    template_name = "dashboard/admin/products/product-create.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "محصول با موفقیت ایجاد شد."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-list")


class AdminProductUpdateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    template_name = "dashboard/admin/products/product-edit.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "محصول با موفقیت ویرایش شد."

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product-edit", kwargs={"pk": self.get_object().pk}
        )


class AdminProductDeleteView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView
):
    template_name = "dashboard/admin/products/product-delete.html"
    queryset = ProductModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:product-list")
    success_message = "محصول با موفقیت حذف شد."
