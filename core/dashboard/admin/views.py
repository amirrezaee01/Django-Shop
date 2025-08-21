from django.shortcuts import render
from django.views.generic import TemplateView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from accounts.models import UserType
from dashboard.permissions import HasCustomerAccessPermison, HasAdminAccessPermison
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from dashboard.admin.forms import AdminPasswordChangeForm, AdminProfileEditForm

from accounts.models import Profile


class AdminDashboardHomeView(LoginRequiredMixin, HasAdminAccessPermison, TemplateView):
    template_name = 'dashboard/admin/home.html'


class AdminSecurityEditView(LoginRequiredMixin, SuccessMessageMixin, HasAdminAccessPermison, auth_views.PasswordChangeView):
    template_name = 'dashboard/admin/profile/security-edit.html'
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy('dashboard:admin:security-edit')
    success_message = "رمز عبور با موفقیت تغییر کرد."


class AdminProfileEditView(LoginRequiredMixin, HasAdminAccessPermison, SuccessMessageMixin, UpdateView):
    template_name = 'dashboard/admin/profile/profile-edit.html'
    form_class = AdminProfileEditForm  # Assuming you have a form for profile editing
    success_url = reverse_lazy('dashboard:admin:profile-edit')
    success_message = "پروفایل با موفقیت به‌روزرسانی شد."

    def get_object(self, queryset=None):

        return Profile.objects.get(user=self.request.user)
