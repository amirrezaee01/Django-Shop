from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    form_class = AuthenticationForm


class LogoutView(auth_views.LogoutView):
    pass
