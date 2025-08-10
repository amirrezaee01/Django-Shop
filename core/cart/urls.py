from django.urls import path, re_path
from .views import *

app_name = 'cart'

urlpatterns = [
    path('session/add-product/', SessionAddProductView.as_view(),
         name='session-add-product'),
    path('session/remove-product/', SessionRemoveProductView.as_view(),
         name='session-remove-product'),
    path('session/update-product-quantity/', SessionUpdateProductQuantityView.as_view(),
         name='session-update-product-quantity'),
    path('session/cart/summary/', SessionCartSummaryView.as_view(),
         name='session-cart-summary'),

]
