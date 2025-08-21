from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from accounts.models import UserType
from dashboard.permissions import HasCustomerAccessPermison, HasAdminAccessPermison


class AdminDashboardHomeView(LoginRequiredMixin, HasAdminAccessPermison, TemplateView):
    template_name = 'dashboard/admin/home.html'
