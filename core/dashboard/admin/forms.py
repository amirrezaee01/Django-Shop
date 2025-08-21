from django.contrib.auth.forms import PasswordChangeForm


class AdminPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        'password_incorrect': "رمز عبور فعلی شما نادرست است.",
        'password_mismatch': "رمزهای عبور جدید مطابقت ندارند.",
        'password_too_similar': "رمز عبور جدید نباید مشابه رمز عبور فعلی باشد.",
        'password_too_short': "رمز عبور جدید باید حداقل 8 کاراکتر باشد.",
        'password_entirely_numeric': "رمز عبور جدید نباید فقط شامل اعداد باشد.",
    }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        field_placeholders = {
            "old_password": "رمز عبور فعلی",
            "new_password1": "رمز عبور جدید",
            "new_password2": "تکرار رمز عبور",
        }

        for field_name, placeholder in field_placeholders.items():
            self.fields[field_name].widget.attrs.update({
                "placeholder": placeholder,
                "class": "form-control",  # Bootstrap styling
                "autocomplete": "off",    # optional: avoid browser autofill
            })
