import requests
import json
import os
from urllib.parse import urlparse


class ZarinPalSandbox:
    _payment_request_url = (
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    )
    _payment_verify_url = (
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
    )
    _payment_page_url = "https://sandbox.zarinpal.com/pg/StartPay/"
    def __init__(self, merchant_id, callback_url):
        if not isinstance(merchant_id, str) or not merchant_id.strip():
            raise ValueError("Set MERCHANT_ID before using the payment demo.")
        parsed_callback = urlparse(callback_url)
        if parsed_callback.scheme not in {"http", "https"} or not parsed_callback.netloc:
            raise ValueError("Set PAYMENT_CALLBACK_URL to an absolute HTTP(S) callback URL.")
        self.merchant_id = merchant_id
        self._callback_url = callback_url

    def payment_request(self, amount, description="پرداختی کاربر"):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": str(amount),
            "CallbackURL": self._callback_url,
            "Description": description,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self._payment_request_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=(5, 20),
        )
        response.raise_for_status()

        return response.json()

    def payment_verify(self, amount, authority):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": amount,
            "Authority": authority,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self._payment_verify_url, headers=headers, data=json.dumps(payload)
        )
        return response.json()

    def generate_payment_url(self, authority):
        return self._payment_page_url + authority


if __name__ == "__main__":
    merchant_id = os.environ.get("MERCHANT_ID", "").strip()
    callback_url = os.environ.get("PAYMENT_CALLBACK_URL", "").strip()
    if not merchant_id or not callback_url:
        raise SystemExit(
            "Set MERCHANT_ID and PAYMENT_CALLBACK_URL in your environment before running this demo."
        )

    zarinpal = ZarinPalSandbox(merchant_id=merchant_id, callback_url=callback_url)
    response = zarinpal.payment_request(15000)

    if response.get("Status") != 100 or not response.get("Authority"):
        raise SystemExit(
            f"Zarinpal payment request failed with status {response.get('Status')!r}."
        )

    print("Zarinpal payment request created.")
    input("proceed to generating payment url?")
    print(zarinpal.generate_payment_url(response["Authority"]))

    input("check the payment?")

    response = zarinpal.payment_verify(15000, response["Authority"])
    print(response)
