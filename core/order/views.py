from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from order.permissions import HasCustomerAccessPermission


class OrderCheckoutView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'order/checkout.html'
