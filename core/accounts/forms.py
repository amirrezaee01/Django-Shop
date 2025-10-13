from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import forms as auth_forms

User = get_user_model()

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="کلمه عبور")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="تکرار کلمه عبور")

    class Meta:
        model = User
        fields = ("email",)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("کلمه عبور و تکرار آن یکسان نیست.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_verified = False  # not verified yet
        if commit:
            user.save()
        return user



class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_verified:
            raise ValidationError(
                "حساب شما فعال نشده است. لطفاً ایمیل خود را بررسی کنید."
            )
