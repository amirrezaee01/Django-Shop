from django.contrib import admin
from .models import PaymentModel


@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "authority_id",
        "ref_id",
        "amount",
        "status",
        "created_date",
        "updated_date",
    )
