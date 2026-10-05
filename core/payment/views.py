from django.shortcuts import render
from django.views.generic import View
from .models import PaymentModel, PaymentStatusType
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from .zarinpal_client import (
    PaymentConfigurationError,
    PaymentGatewayError,
    ZarinPalSandbox,
)
from order.models import OrderModel, OrderStatusType
from django.db import transaction
from django.http import HttpResponse

# Create your views here.


class PaymentVerifyView(View):
    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        status = request.GET.get("Status")

        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)
        order = OrderModel.objects.get(payment=payment_obj)
        try:
            zarin_pal = ZarinPalSandbox()
            response = zarin_pal.payment_verify(
                int(payment_obj.amount), payment_obj.authority_id
            )
        except (PaymentConfigurationError, PaymentGatewayError):
            return HttpResponse("Payment verification is temporarily unavailable.", status=503)
        status_code = response["Status"]
        ref_id = response.get("RefID") if status_code in {100, 101} else None
        if status_code in {100, 101} and ref_id is None:
            return HttpResponse("Payment verification returned an invalid response.", status=502)

        with transaction.atomic():
            payment_obj.ref_id = ref_id
            payment_obj.response_code = status_code
            payment_obj.status = (
                PaymentStatusType.success.value
                if status_code in {100, 101}
                else PaymentStatusType.failed.value
            )
            payment_obj.response_json = response
            payment_obj.save()

            order.status = (
                OrderStatusType.success.value
                if status_code in {100, 101}
                else OrderStatusType.failed.value
            )
            order.save()

        return redirect(
            reverse_lazy("order:completed")
            if status_code in {100, 101}
            else reverse_lazy("order:failed")
        )
