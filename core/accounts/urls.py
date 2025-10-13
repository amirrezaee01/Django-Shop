from django.urls import path
from .views import LoginView, LogoutView, SignupView, ActivateAccount

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("activate/<uidb64>/<token>/", ActivateAccount.as_view(), name="activate"),
]
