from django.views.generic import (
    UpdateView,
    DeleteView,
    CreateView,
    ListView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission

from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from core.query_utils import apply_ordering, bounded_page_size, filter_partial_id
from order.models import OrderModel, OrderStatusType


class AdminOrderListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/orders/order-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return bounded_page_size(self.request, self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.select_related("user", "payment", "coupon")
        if search_q := self.request.GET.get("q"):
            queryset = filter_partial_id(queryset, search_q)
        if status := self.request.GET.get("status"):
            try:
                queryset = queryset.filter(status=int(status))
            except ValueError:
                return queryset.none()
        queryset = apply_ordering(
            queryset, self.request.GET.get("order_by"), {"id", "created_date", "total_price", "status"}
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["page_obj"].paginator.count
        context["status_types"] = OrderStatusType.choices
        return context


class AdminOrderDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/orders/order-detail.html"

    def get_queryset(self):
        return OrderModel.objects.all()


class AdminOrderInvoiceView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/orders/order-invoice.html"

    def get_queryset(self):
        return OrderModel.objects.filter(status=OrderStatusType.success.value)
