import cv2
import os
import csv
import numpy as np
import pygame
from PIL import Image
import customtkinter as ctk
from tensorflow.keras.models import load_model

from vision.mask_detection import predict_mask
from vision.face_detection import detect_faces_dnn


# =========================================================
# MAIN REGISTRATION FUNCTION
# =========================================================
def take_images(app, user_id, name, phone, deposit, pin, ui_label):
    """
    Capture face images ONLY when NO MASK is detected
    Then train per-user recognition model.
    Pipes the camera feed directly to a CustomTkinter ui_label.

    Returns:
        (status, message)
    """

    Id = str(user_id)

    try:
        initial_deposit = float(deposit)
    except:
        initial_deposit = 0.0

    # ---------- Duplicate check ----------
    if Id in app.data:
        return 0, "User already exists"

    # =====================================================
    # Load mask model
    # =====================================================
    model = app.mask_model
    if model is None:
        try:
            model = load_model(
                "models/mask_detector_model.h5",
                compile=False
            )
            app.mask_model = model
        except:
            return 0, "Mask model load failed"

    # =====================================================
    # Sound init
    # =====================================================
    try:
        pygame.mixer.init()
    except:
        pass

    sound_file = "auth/alert_more_than_2.mp3"

    # =====================================================
    # Create user image folder
    # =====================================================
    base_folder = "TrainingImage"
    user_folder = os.path.join(base_folder, Id)
    os.makedirs(user_folder, exist_ok=True)

    # =====================================================
    # Camera
    # =====================================================
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    # =====================================================
    # Face detector (DNN)
    # =====================================================
    net = cv2.dnn.readNetFromCaffe(
        "models/deploy.prototxt.txt",
        "models/res10_300x300_ssd_iter_140000.caffemodel"
    )

    sample_num = 0

    print("📸 Starting registration...")

    while True:

        ret, img = cam.read()
        if not ret:
            break

        faces = detect_faces_dnn(img, net)

        # ---------- Crowd check ----------
        if len(faces) > 2:

            try:
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except:
                pass

            pygame.time.delay(2000)

            cam.release()
            return 0, "More than 2 people detected"

        # =================================================
        # Process faces
        # =================================================
        for (x, y, w, h) in faces:

            if w <= 0 or h <= 0:
                continue

            pad = 20
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(img.shape[1], x + w + pad)
            y2 = min(img.shape[0], y + h + pad)

            face_color = img[y1:y2, x1:x2]

            if face_color.size == 0:
                continue

            # ---------- Prepare for mask model ----------
            face_rgb = cv2.cvtColor(face_color, cv2.COLOR_BGR2RGB)

            face_input = cv2.resize(
                face_rgb,
                app.model_input_size
            )

            face_input = face_input.astype("float32") / 255.0
            face_input = np.expand_dims(face_input, axis=0)

            # ---------- Mask prediction ----------
            mask_prob, no_mask_prob = predict_mask(
                model,
                face_input
            )

            NO_MASK_THRESHOLD = 0.6

            # =================================================
            # SAVE ONLY IF NO MASK
            # =================================================
            if no_mask_prob > NO_MASK_THRESHOLD:

                label = f"No Mask ({no_mask_prob*100:.1f}%)"
                color = (0, 0, 255)

                filename = os.path.join(
                    user_folder,
                    f"{name}.{Id}.{sample_num}.jpg"
                )

                cv2.imwrite(filename, face_color)
                sample_num += 1

                if sample_num >= 100:
                    break

            else:
                label = f"Mask ({mask_prob*100:.1f}%)"
                color = (0, 255, 0)

            # ---------- Draw ----------
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)

            cv2.putText(
                img,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

        if sample_num >= 100:
            break

        cv2.putText(
            img,
            f"Captures: {sample_num}/100",
            (420, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        # =====================================================
        # RENDER TO CUSTOMTKINTER UI LABEL INSTED OF CV2.IMSHOW
        # =====================================================
        # 1. Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 2. Convert to PIL Image
        pil_img = Image.fromarray(img_rgb)
        
        # 3. Create CTkImage wrapper
        ctk_img = ctk.CTkImage(light_image=pil_img, size=(640, 480))
        
        # 4. Set image on the label
        ui_label.configure(image=ctk_img)
        ui_label.image = ctk_img  # Prevent garbage collection
        
        # 5. Force UI to redraw
        ui_label.update()
        
        # Small wait for responsiveness
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cam.release()

    # =====================================================
    # If images captured → train model
    # =====================================================
    if sample_num > 0:

        success, msg = train_user_model(Id)

        if not success:
            return 0, msg

        # ---------- Save details ----------
        os.makedirs("Details", exist_ok=True)

        csv_file = "Details/Details.csv"
        file_exists = os.path.exists(csv_file)

        with open(csv_file, "a+", newline="") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(
                    ["Id", "Name", "Phone", "Initial_Deposit"]
                )

            writer.writerow(
                [Id, name, phone, initial_deposit]
            )

        return 1, f"Registration successful for ID {Id}"

    else:
        return 0, "No images captured"


# =========================================================
# TRAIN PER-USER 1:1 MODEL
# =========================================================
def train_user_model(user_id):
    if not user_id:
        return False, "No user ID provided for 1:1 training"

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(
        "models/haarcascade_frontalface_default.xml"
    )

    faces = []
    labels = []

    user_path = os.path.join("TrainingImage", str(user_id))
    
    if not os.path.exists(user_path) or not os.path.isdir(user_path):
        return False, f"Image directory for user {user_id} not found"

    for file in os.listdir(user_path):
        if not file.lower().endswith((".jpg", ".png")):
            continue

        img_path = os.path.join(user_path, file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        detected = detector.detectMultiScale(img, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

        for (x, y, w, h) in detected:
            faces.append(img[y:y+h, x:x+w])
            labels.append(1)  # Dummy label 1, since it's an isolated 1:1 model

    if not faces:
        return False, "Training failed: No faces detected in user captures"

    recognizer.train(faces, np.array(labels, dtype=np.int32))

    os.makedirs("TrainingImageLabel", exist_ok=True)
    model_path = f"TrainingImageLabel/Trainer_{user_id}.yml"
    recognizer.save(model_path)

    print(f"✅ Isolated User Model saved: {model_path}")

    return True, "User specialized model trained successfully"