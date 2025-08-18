from django.urls import path, include
from .views import DashboardHomeView

app_name = 'dashboard'

urlpatterns = [
    path('home/', DashboardHomeView.as_view(), name='home'),

    # ✅ important: include as (module, app_name), namespace
    path('admin/', include(('dashboard.admin.urls', 'admin'), namespace='admin')),
    path('customer/', include(('dashboard.customer.urls',
         'customer'), namespace='customer')),
]
