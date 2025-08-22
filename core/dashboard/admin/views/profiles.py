from django.views.generic import View, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from django.contrib.auth import views as auth_views
from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from accounts.models import Profile
from django.shortcuts import redirect
from django.contrib import messages


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


class AdminProfileImageEditView(LoginRequiredMixin, HasAdminAccessPermison, SuccessMessageMixin, UpdateView):
    http_method_names = ['post']
    model = Profile
    fields = ['image']

    success_url = reverse_lazy('dashboard:admin:profile-edit')
    success_message = "تصویر پروفایل با موفقیت به‌روزرسانی شد."

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    def form_invalid(self, form):
        messages.error(self.request, "خطا در به‌روزرسانی تصویر پروفایل.")
        return redirect(self.success_url)
