import cv2
import os
import time
import numpy as np
import pygame
from PIL import Image
import customtkinter as ctk
from datetime import datetime
from tensorflow.keras.models import load_model

from vision.mask_detection import predict_mask
from auth.sms_alert import send_alert_sms, send_crowd_alert
from vision.face_detection import detect_faces_dnn


def verify_face(app, user_id, ui_label):

    user_id = str(user_id)

    # ======================================================
    # LOAD ISOLATED 1:1 USER MODEL
    # ======================================================
    model_path = f"TrainingImageLabel/Trainer_{user_id}.yml"

    if not os.path.exists(model_path):
        print(f"[ERROR] Biometric data missing for user {user_id}")
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)

    # ======================================================
    # USE SECURE DNN FOR FACE DETECTION ROBUST TO MASKS
    # ======================================================
    net = cv2.dnn.readNetFromCaffe(
        "models/deploy.prototxt.txt",
        "models/res10_300x300_ssd_iter_140000.caffemodel"
    )

    # ======================================================
    # LOAD MASK MODEL
    # ======================================================
    mask_model = app.mask_model
    if mask_model is None:
        mask_model = load_model(
            "models/mask_detector_model.h5",
            compile=False
        )
        app.mask_model = mask_model

    # ======================================================
    # CAMERA
    # ======================================================
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    # ======================================================
    # AUDIO
    # ======================================================
    try:
        pygame.mixer.init()
    except:
        pass

    REMOVE_MASK_AUDIO = "auth/remove_mask.mp3"
    CROWD_AUDIO = "auth/alert_more_than_2.mp3"

    unknown_folder = "Unknown_Face_Captures"
    os.makedirs(unknown_folder, exist_ok=True)

    # ======================================================
    # STATE VARIABLES
    # ======================================================
    VISIBILITY_TIME = 5
    REMOVAL_TIME = 30
    VERIFY_TIMEOUT = 15

    visibility_start = time.time()
    removal_start = None
    verify_start = None

    state = "VISIBILITY"

    last_warning = None

    print(f"[INFO] Verification started for ID {user_id}")

    # ======================================================
    # MAIN LOOP
    # ======================================================
    while True:

        ret, img = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # --------------------------------------------------
        # ROBUST FACE DETECTION WITH DNN
        # --------------------------------------------------
        faces = detect_faces_dnn(img, net)

        # --------------------------------------------------
        # NO PERSON CHECK
        # --------------------------------------------------
        if len(faces) == 0:
            cv2.putText(img, "NO PERSON IN THE FRAME", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # --------------------------------------------------
        # CROWD CHECK
        # --------------------------------------------------
        elif len(faces) >= 2:
            if last_warning != "crowd":
                print("[WARNING] More than 2 people detected")
                last_warning = "crowd"

            try:
                pygame.mixer.music.load(CROWD_AUDIO)
                pygame.mixer.music.play()
            except:
                pass

            cv2.putText(img, "ONLY ONE PERSON ALLOWED", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=(640, 480))
            ui_label.configure(image=ctk_img)
            ui_label.image = ctk_img
            ui_label.update()
            
            pygame.time.delay(2000)
            cam.release()
            return False

        # --------------------------------------------------
        # GLOBAL TIMER RENDERING (Always top layer!)
        # --------------------------------------------------
        if state == "VERIFY" and verify_start is not None:
            time_elapsed = time.time() - verify_start
            remaining = max(0, int(VERIFY_TIMEOUT - time_elapsed))
            cv2.putText(img, f"Timeout: {remaining}s", (450, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Global Timeout Trigger
            if time_elapsed > VERIFY_TIMEOUT:
                print("[WARNING] Verification timeout → OTP")
                filename = os.path.join(unknown_folder, f"Timeout_{datetime.now():%Y%m%d_%H%M%S}.jpg")
                cv2.imwrite(filename, img)
                send_alert_sms(filename, "Verification timeout")
                cam.release()
                return "otp"

        elif state == "REMOVAL" and removal_start is not None:
            time_elapsed = time.time() - removal_start
            if time_elapsed > REMOVAL_TIME:
                print("[WARNING] Mask not removed — session terminated")
                cam.release()
                return False


        mask_present = False

        # ==================================================
        # PROCESS FACES
        # ==================================================
        for (x, y, w, h) in faces:

            # Enforce bounds
            pad = 20
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(img.shape[1], x + w + pad)
            y2 = min(img.shape[0], y + h + pad)

            face = img[y1:y2, x1:x2]
            if face.size == 0: continue

            # ---------- MASK PREDICTION ----------
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face_input = cv2.resize(face_rgb, app.model_input_size)
            face_input = face_input.astype("float32") / 255.0
            face_input = np.expand_dims(face_input, axis=0)

            mask_prob, no_mask_prob = predict_mask(mask_model, face_input)

            NO_MASK_THRESHOLD = 0.6
            if no_mask_prob > NO_MASK_THRESHOLD:
                mask_present = False
                label = f"No Mask {no_mask_prob*100:.1f}%"
                color = (0, 255, 0)
            else:
                mask_present = True
                label = f"Mask {mask_prob*100:.1f}%"
                color = (0, 0, 255)

            # ---------- DRAW FACE BOX ----------
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # ==================================================
            # 🔵 VISIBILITY CHECK
            # ==================================================
            if state == "VISIBILITY":

                if not mask_present:
                    state = "VERIFY"
                    verify_start = time.time()
                    print("[INFO] No mask detected → Verification")

                elif time.time() - visibility_start > VISIBILITY_TIME:
                    state = "REMOVAL"
                    removal_start = time.time()

                    if last_warning != "mask":
                        print("[WARNING] Mask detected — waiting removal")
                        last_warning = "mask"

                    try:
                        pygame.mixer.music.load(REMOVE_MASK_AUDIO)
                        print("Tried to Play Mask Audio")
                        pygame.mixer.music.play()
                    except:
                        pass

            # ==================================================
            # 🟠 REMOVAL WINDOW
            # ==================================================
            elif state == "REMOVAL":

                cv2.putText(img, "REMOVE MASK", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

                if not mask_present:
                    state = "VERIFY"
                    verify_start = time.time()
                    print("[INFO] Mask removed → Verification")

            # ==================================================
            # 🟢 VERIFICATION
            # ==================================================
            elif state == "VERIFY":

                # Extract proper gray face for LBPH mapping
                face_gray = gray[y:y+h, x:x+w]
                if face_gray.size == 0: continue
                
                try:
                    face_gray = cv2.resize(face_gray, (128, 128))
                    predicted_id, conf = recognizer.predict(face_gray)
                except:
                    conf = 999

                print(f"[INFO] 1:1 Verification Distance: {conf:.2f}")

                STRICT_THRESHOLD = 75

                if conf < STRICT_THRESHOLD:
                    print("[SUCCESS] Face verified securely")
                    cam.release()
                    return True
                else:
                    if last_warning != "unrecognized":
                        print(f"[WARNING] Face not matched for Id.(conf={conf:.1f})")
                        last_warning = "unrecognized"

                    cv2.putText(img, "FACE NOT MATCHED FOR ID", (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        # =====================================================
        # RENDER UI
        # =====================================================
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        ctk_img = ctk.CTkImage(light_image=pil_img, size=(640, 480))
        
        ui_label.configure(image=ctk_img)
        ui_label.image = ctk_img
        ui_label.update()

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cam.release()