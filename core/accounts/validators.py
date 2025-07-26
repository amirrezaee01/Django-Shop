from django.core.exceptions import ValidationError
import re


def validate_iranian_phone_number(value):
    pattern = r'^(?:\+98|0)?9\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Enter a valid Iranian phone number (e.g., 09123456789 or +989123456789).')
