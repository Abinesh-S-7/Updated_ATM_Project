# auth/sms_alert.py

import cloudinary
import cloudinary.uploader
from twilio.rest import Client

# ==============================
# Cloudinary Config
# ==============================
cloudinary.config(
    cloud_name="",
    api_key="",
    api_secret=""
)

# ==============================
# Twilio Config
# ==============================
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""
TO_PHONE_NUMBER = ""


# ==============================
# Upload Image
# ==============================
def upload_to_cloudinary(image_path):

    try:
        result = cloudinary.uploader.upload(image_path)
        return result["secure_url"]

    except Exception as e:
        print("Cloudinary upload failed:", e)
        return None


# ==============================
# Send Image Alert
# ==============================
def send_alert_sms(image_path, reason="Security Alert"):

    try:
        image_url = upload_to_cloudinary(image_path)

        if not image_url:
            return False

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        message = client.messages.create(
            body=f"🚨 {reason}",
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER,
            media_url=[image_url]
        )

        print("✅ Alert sent:", message.sid)
        return True

    except Exception as e:
        print("❌ Alert SMS failed:", e)
        return False


# ==============================
# Multiple People Alert
# ==============================
def send_crowd_alert():

    try:
        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        message = client.messages.create(
            body="⚠️ More than 2 people detected in ATM!",
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )

        print("✅ Crowd alert sent:", message.sid)

    except Exception as e:
        print("❌ Crowd alert failed:", e)