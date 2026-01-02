from django.conf import settings
from zarinpal import ZarinPal
from utils.Config import Config

config = Config(
    merchant_id=settings.ZARINPAL_MERCHANT_ID,
    sandbox=settings.ZARINPAL_SANDBOX
)
zarinpal = ZarinPal(config)

def create_payment(amount, description, callback_url, email=None, mobile=None):
    """Create a payment request and return the payment URL + authority code."""
    result = zarinpal.payment_gateway.create({
        "amount": amount,
        "description": description,
        "callback_url": callback_url,
        "email": email,
        "mobile": mobile,
    })
    return result
