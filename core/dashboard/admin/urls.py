from django.urls import path
from .views import AdminDashboardHomeView

app_name = 'admin'

urlpatterns = [
    path('home/', AdminDashboardHomeView.as_view(), name='home'),
]
