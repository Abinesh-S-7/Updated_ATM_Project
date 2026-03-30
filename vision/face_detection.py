import cv2
import numpy as np


# =========================================================
# Load DNN Face Detector
# =========================================================
def load_dnn_model(
    prototxt_path="models/deploy.prototxt.txt",
    model_path="models/res10_300x300_ssd_iter_140000.caffemodel"
):
    """
    Load OpenCV DNN face detector

    Returns:
        net -> loaded DNN model
    """
    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    return net


# =========================================================
# DNN Face Detection (HIGH ACCURACY)
# =========================================================
def detect_faces_dnn(frame, net, conf_threshold=0.6):
    """
    Detect faces using OpenCV DNN model

    Parameters:
        frame -> BGR image
        net -> DNN model
        conf_threshold -> confidence threshold

    Returns:
        list of faces: [(x, y, w, h), ...]
    """

    (h, w) = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(
        frame,
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0)
    )

    net.setInput(blob)
    detections = net.forward()

    faces = []

    for i in range(detections.shape[2]):

        confidence = detections[0, 0, i, 2]

        if confidence > conf_threshold:

            box = detections[0, 0, i, 3:7] * np.array(
                [w, h, w, h]
            )

            x1, y1, x2, y2 = box.astype("int")

            # Clamp values inside frame
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            faces.append(
                (x1, y1, x2 - x1, y2 - y1)
            )

    return faces


# =========================================================
# Haar Cascade Face Detection (FAST)
# =========================================================
def load_haar_model(
    cascade_path="models/haarcascade_frontalface_default.xml"
):
    """
    Load Haar Cascade model
    """
    return cv2.CascadeClassifier(cascade_path)


def detect_faces_haar(
    frame,
    cascade,
    scale_factor=1.1,
    min_neighbors=5
):
    """
    Detect faces using Haar Cascade

    Returns:
        list of faces: [(x, y, w, h), ...]
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors
    )

    return faces


# =========================================================
# Utility: Draw Bounding Boxes
# =========================================================
def draw_faces(
    frame,
    faces,
    color=(0, 255, 0),
    thickness=2
):
    """
    Draw rectangles around detected faces
    """

    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            color,
            thickness
        )

    return frame


# =========================================================
# Utility: Extract Face Regions
# =========================================================
def extract_face_regions(
    frame,
    faces,
    padding=20
):
    """
    Extract cropped face images with padding

    Returns:
        list of cropped face images
    """

    h, w = frame.shape[:2]
    face_images = []

    for (x, y, fw, fh) in faces:

        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w, x + fw + padding)
        y2 = min(h, y + fh + padding)

        face = frame[y1:y2, x1:x2]

        if face.size > 0:
            face_images.append(face)

    return face_images