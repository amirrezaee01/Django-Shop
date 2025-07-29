from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('product/grid/', ShopProductGridView.as_view(), name='product-grid'),
    path('product/<slug:slug>/detail',
         ShopProductDetailView.as_view(), name='product-detail'),
]
