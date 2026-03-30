# auth/otp_verify.py

from twilio.rest import Client
import random
from datetime import datetime

# ==============================
# Twilio Configuration
# ==============================
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""

# OTP storage (in-memory)
last_otp = None
last_otp_time = None
OTP_VALIDITY = 300  # 5 minutes


# ==============================
# GENERATE OTP
# ==============================
def generate_otp():
    return str(random.randint(100000, 999999))


# ==============================
# SEND OTP SMS
# ==============================
def send_otp_sms(phone_number):
    global last_otp, last_otp_time
    phone_number=""

    try:
        otp = generate_otp()

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        message = client.messages.create(
            body=f"🔐 ATM OTP: {otp} (valid 5 minutes)",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        print("✅ OTP sent:", message.sid)

        last_otp = otp
        last_otp_time = datetime.now()

        return otp

    except Exception as e:
        print("❌ OTP send failed:", e)
        return None


# ==============================
# VERIFY OTP
# ==============================
def verify_otp(entered_otp):
    global last_otp, last_otp_time

    if not last_otp:
        return False

    # Check expiry
    if (datetime.now() - last_otp_time).total_seconds() > OTP_VALIDITY:
        print("❌ OTP expired")
        return False

    return entered_otp == last_otp