from django.urls import path,re_path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('product/grid/', ShopProductGridView.as_view(), name='product-grid'),
    re_path(r"product/(?P<slug>[-\w]+)/detail/",ShopProductDetailView.as_view(),name="product-detail"),
    path("add-or-remove-wishlist/",AddOrRemoveWishlistView.as_view(),name="add-or-remove-wishlist")


]