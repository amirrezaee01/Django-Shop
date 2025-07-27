from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView


class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = AuthenticationForm
