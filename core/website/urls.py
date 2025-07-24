from django.urls import path
from .views import *

app_name = 'website'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactViews.as_view(), name='contact'),
]
