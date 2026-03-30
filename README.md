# AI-Powered Smart ATM Security System

The AI-Powered Smart ATM Security System is a cutting-edge, high-security interactive banking kiosk application. It leverages deep learning (DNN) face detection, isolated 1:1 biometric verification, live mask detection, real-time audio/sms alerts, and Two-Factor Authentication (OTP via Twilio) to provide unparalleled security and flexibility during ATM transactions.

## Features

- **Interactive Registration Wizard:** A multi-step UI flow with per-page live validation to securely register new accounts and card credentials seamlessly without cluttered forms.
- **1:1 Biometric Verification:** Instantly trains an isolated Local Binary Patterns Histogram (LBPH) model precisely tied to each unique user. During login, it exclusively loads only the claimant's localized mathematical model, guaranteeing fast and highly secure 1:1 identity verification rather than scanning massive global datasets.
- **Deep Neural Network Mask & Face Detection:** Uses advanced OpenCV DNN processing combined with a custom Keras (`.h5`) AI model to robustly and reliably detect faces in varying conditions and determine mask probabilities in real-time.
- **Crowd Control Alerts:** Automatically detects if more than one individual attempts to peer into the camera frame. It instantly safeguards the session by terminating visibility, playing a localized audio alarm, and logging the event to block shoulder-surfing.
- **OTP Fallback Protocol:** If biometric verification experiences a timeout (or if multiple failures occur), the camera elegantly transitions into a completely integrated, native One-Time-Password (OTP) frame UI. It automatically dispatches a strict OTP code via Twilio SMS to the user's previously registered mobile phone number.
- **Dynamic Graphical User Interface:** Powered exclusively by `customtkinter`, delivering a sleek, modern, touch-friendly cinematic interface reminiscent of next-generation physical ATM kiosks instead of developer system prompts.

## Quick Start Setup Instructions

### 1. Requirements
Ensure you are using Python 3.8 to 3.11. (Higher versions might occasionally experience missing Keras dependencies depending on your hardware profile).

```bash
git clone https://github.com/Abinesh-S-7/Updated_ATM_Project.git
cd Updated_ATM_Project
pip install -r requirements.txt
```

### 2. Configure Security Microservices (Optional but highly recommended)
In order to use the OTP sending capabilities and cloud logging, locate `auth/sms_alert.py` and `auth/otp_verify.py` and input your developer API configurations:
- **Twilio**: Account SID, Auth Token, and designated Phone Numbers.
- **Cloudinary**: Cloud name, API keys, and secrets.

### 3. Execution
Simply invoke the main entry point to spawn the graphical interface!

```bash
python main.py
```

## Application Architecture

- **`main.py` / `ui/app.py`:** Core Application loop and centralized screen frame router.
- **`vision/`:** Contains highly specialized camera verification loops (`registration_cam.py`, `verification_cam.py`) mapped to Deep Neural Networks (`face_detection.py`) and Keras evaluation models (`mask_detection.py`).
- **`auth/`:** Manages OTP mathematics, unified Twilio SMS dispatch interfaces, and remote Cloudinary uploads.
- **`data/`:** Secures and handles localized encrypted JSON data storage and traditional CSV logging infrastructure to securely persist variables.
- **`models/`:** Storage repository hosting predefined OpenCV XML configurations and massive `Caffe` architecture topologies.

## Future Endeavors

- Extend deep learning modules to incorporate advanced Liveness Detection to defeat 2D photo spoofing attacks.
- Standardize full database bridging for scalable external deployments to authentic bank environments.
