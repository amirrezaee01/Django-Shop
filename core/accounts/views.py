from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm, SignupForm
from django.views.generic import FormView, View
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages
from django.core.exceptions import ValidationError
from .tokens import account_activation_token
from django.shortcuts import redirect

User = get_user_model()


# -----------------------------
# Login View
# -----------------------------
class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    form_class = AuthenticationForm


# -----------------------------
# Logout View
# -----------------------------
class LogoutView(auth_views.LogoutView):
    pass


# -----------------------------
# Signup View
# -----------------------------
class SignupView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        current_site = get_current_site(self.request)
        subject = "فعال‌سازی حساب کاربری شما"
        message = render_to_string("accounts/email_verification.html", {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        })
        send_mail(subject, message, None, [user.email], fail_silently=False)
        return super().form_valid(form)

# -----------------------------
# Activation View
# -----------------------------
class ActivateAccount(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None
        if user and account_activation_token.check_token(user, token):
            user.is_verified = True
            user.save()
            return redirect("accounts:login")
        return redirect("accounts:signup")