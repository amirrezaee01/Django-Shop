from django.urls import path
from .views import *

app_name = 'admin'

urlpatterns = [
    path('home/', AdminDashboardHomeView.as_view(), name='home'),
    path('security-edit/', AdminSecurityEditView.as_view(), name='security-edit'),
    path('profile-edit/', AdminProfileEditView.as_view(), name='profile-edit'),

]
