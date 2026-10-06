from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import UserType


class DashboardHomeView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Send authenticated users to the dashboard for their account role."""
        user = request.user
        if (
            user.type == UserType.admin.value
            or user.is_staff
            or user.is_superuser
        ):
            return redirect("dashboard:admin:home")
        if user.type == UserType.customer.value:
            return redirect("dashboard:customer:home")
        return redirect("accounts:login")
