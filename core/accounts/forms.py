from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError


class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        # if not user.is_verified:
        #     raise ValidationError(
        #         "This account is not verified. Please check your email for verification instructions."
        #     )
