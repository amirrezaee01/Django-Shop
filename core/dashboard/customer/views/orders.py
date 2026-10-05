from django.views.generic import (
    UpdateView,
    DeleteView,
    CreateView,
    ListView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission

from dashboard.customer.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from core.query_utils import apply_ordering, bounded_page_size, filter_partial_id
from order.models import OrderModel, OrderStatusType


class CustomerOrderListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    template_name = "dashboard/customer/orders/order-list.html"
    paginate_by = 5

    def get_paginate_by(self, queryset):
        return bounded_page_size(self.request, self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.filter(user=self.request.user).select_related("payment", "coupon")
        if search_q := self.request.GET.get("q"):
            queryset = filter_partial_id(queryset, search_q)
        if status := self.request.GET.get("status"):
            try:
                queryset = queryset.filter(status=int(status))
            except ValueError:
                return queryset.none()
        return apply_ordering(
            queryset, self.request.GET.get("order_by"), {"id", "created_date", "total_price", "status"}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["page_obj"].paginator.count
        context["status_types"] = OrderStatusType.choices
        return context


class CustomerOrderDetailView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    template_name = "dashboard/customer/orders/order-detail.html"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)


class CustomerOrderInvoiceView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    template_name = "dashboard/customer/orders/order-invoice.html"

    def get_queryset(self):
        return OrderModel.objects.filter(
            user=self.request.user, status=OrderStatusType.success.value
        )
