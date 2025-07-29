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
