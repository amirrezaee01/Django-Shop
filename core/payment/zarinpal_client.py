import requests
import json
from django.conf import settings


class PaymentConfigurationError(ValueError):
    """Raised when payment configuration required to start checkout is absent."""


class PaymentGatewayError(RuntimeError):
    """Raised when the gateway cannot create a valid payment request."""


class ZarinPalSandbox:
    _payment_request_url = (
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    )
    _payment_verify_url = (
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
    )
    _payment_page_url = "https://sandbox.zarinpal.com/pg/StartPay/"

    def __init__(self, merchant_id=None):
        self.merchant_id = settings.MERCHANT_ID if merchant_id is None else merchant_id
        if not isinstance(self.merchant_id, str) or not self.merchant_id.strip():
            raise PaymentConfigurationError(
                "Payments are not configured. Set MERCHANT_ID before accepting checkout."
            )

    def payment_request(self, amount, description="پرداختی کاربر", callback_url=None):
        callback_url = callback_url or getattr(settings, "PAYMENT_CALLBACK_URL", "")
        if not callback_url:
            raise PaymentConfigurationError(
                "Payments are not configured. Set PAYMENT_CALLBACK_URL or provide a callback URL."
            )
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": str(amount),
            "CallbackURL": callback_url,
            "Description": description,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self._payment_request_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=(5, 20),
            )
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise PaymentGatewayError(
                "The payment provider could not be reached. Your cart has not been cleared."
            ) from exc

        if not isinstance(result, dict) or str(result.get("Status")) != "100":
            raise PaymentGatewayError(
                "The payment provider rejected the payment request. Your cart has not been cleared."
            )
        authority = result.get("Authority")
        if not isinstance(authority, str) or not authority.strip():
            raise PaymentGatewayError(
                "The payment provider returned no payment authority. Your cart has not been cleared."
            )
        result["Authority"] = authority.strip()
        return result

    def payment_verify(self, amount, authority):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": amount,
            "Authority": authority,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self._payment_verify_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=(5, 20),
            )
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise PaymentGatewayError(
                "The payment provider could not verify the payment. Please retry shortly."
            ) from exc

        if not isinstance(result, dict):
            raise PaymentGatewayError("The payment provider returned an invalid verification response.")
        try:
            result["Status"] = int(result["Status"])
        except (KeyError, TypeError, ValueError) as exc:
            raise PaymentGatewayError("The payment provider returned an invalid verification response.") from exc
        if result["Status"] in {100, 101}:
            try:
                result["RefID"] = int(result["RefID"])
            except (KeyError, TypeError, ValueError) as exc:
                raise PaymentGatewayError(
                    "The payment provider returned an invalid verification response."
                ) from exc
        return result

    def generate_payment_url(self, authority):
        return f"{self._payment_page_url}{authority}"
