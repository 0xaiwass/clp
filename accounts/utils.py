import random, hashlib
from .models import OTPCode
from utils import send_otp_code  # your existing SMS function

def generate_and_send_otp(phone, session_key):
    """Generate, hash, save, and send an OTP to a phone number."""
    random_code = str(random.randint(100000, 999999))
    otp_hash = hashlib.sha256(random_code.encode()).hexdigest()

    OTPCode.objects.filter(phone=phone).delete()  # remove old OTPs
    OTPCode.objects.create(
        phone=phone,
        code=otp_hash,
        session_key=session_key
    )

    send_otp_code(phone, random_code)  # SMS sending
    return True