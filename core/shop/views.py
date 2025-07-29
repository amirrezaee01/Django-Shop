from django.shortcuts import render
from .models import ProductModel, ProductStatusType
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
)
# Create your views here.


class ShopProductGridView(ListView):
    template_name = 'shop/product_grid.html'
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value)
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.queryset.count()
        return context
