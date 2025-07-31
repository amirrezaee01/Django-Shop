from django.shortcuts import render
from .models import ProductModel, ProductStatusType, ProductCategoryModel
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
)
# Create your views here.


class ShopProductGridView(ListView):
    template_name = 'shop/product_grid.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value)
        if search_q := self.request.GET.get('q'):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get('category_id'):
            queryset = queryset.filter(category__id=category_id)
        return queryset  # <-- Add this line

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.get_queryset().count()
        context['categories'] = ProductCategoryModel.objects.filter(
            productmodel__status=ProductStatusType.publish.value).distinct()
        return context


class ShopProductDetailView(DetailView):
    template_name = 'shop/product_detail.html'
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value)
