from django.views.generic import UpdateView,DeleteView,CreateView,ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission

from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from core.query_utils import apply_ordering, bounded_page_size
from review.models import ReviewModel,ReviewStatusType

class AdminReviewListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/reviews/review-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return bounded_page_size(self.request, self.paginate_by)

    def get_queryset(self):
        queryset = ReviewModel.objects.select_related("user", "product")
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(product__title__icontains=search_q)
        if status := self.request.GET.get("status"):
            try:
                queryset = queryset.filter(status=int(status))
            except ValueError:
                return queryset.none()
        queryset = apply_ordering(
            queryset,
            self.request.GET.get("order_by"),
            {"created_date", "updated_date", "rate", "status", "product__title", "user__email"},
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["page_obj"].paginator.count
        context["status_types"] = ReviewStatusType.choices
        return context

class AdminReviewEditView(LoginRequiredMixin, HasAdminAccessPermission,SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/reviews/review-edit.html"
    queryset = ReviewModel.objects.all()
    form_class = ReviewForm
    success_message = "تغییرات با موفقیت اعمال شد"

    def get_success_url(self) -> str:
        return reverse_lazy("dashboard:admin:review-edit",kwargs={"pk":self.kwargs.get("pk")})
