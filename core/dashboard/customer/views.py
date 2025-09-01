from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from accounts.models import UserType
from dashboard.permissions import HasCustomerAccessPermission, HasAdminAccessPermission


class CustomerDashboardHomeView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'dashboard/customer/home.html'
