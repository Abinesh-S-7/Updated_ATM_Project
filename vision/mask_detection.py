import cv2
import numpy as np
from tensorflow.keras.models import load_model


# =========================================================
# Load Mask Detection Model
# =========================================================
def load_mask_model(model_path="models\mask_detector_model.h5"):
    """
    Load trained mask detection model

    Returns:
        model or None
    """
    try:
        model = load_model(model_path, compile=False)
        print("✅ Mask model loaded")
        return model
    except Exception as e:
        print(f"❌ Failed to load mask model: {e}")
        return None


# =========================================================
# Preprocess Face for Model Input
# =========================================================
def preprocess_face(face_img, target_size=(224, 224)):
    """
    Prepare face image for prediction

    Parameters:
        face_img -> BGR image (OpenCV format)
        target_size -> model input size

    Returns:
        preprocessed image (1, H, W, 3)
    """

    if face_img is None or face_img.size == 0:
        return None

    # Convert BGR → RGB
    face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

    # Resize to model input
    face_resized = cv2.resize(face_rgb, target_size)

    # Normalize
    face_norm = face_resized.astype("float32") / 255.0

    # Add batch dimension
    face_input = np.expand_dims(face_norm, axis=0)

    return face_input


# =========================================================
# Predict Mask / No Mask
# =========================================================
def predict_mask(model, face_for_model):
    """
    Predict mask probabilities

    Works with:
        ✔ Sigmoid output (1 neuron)
        ✔ Softmax output (2 neurons)

    Returns:
        mask_prob, no_mask_prob
    """

    if model is None or face_for_model is None:
        return 0.0, 0.0

    pred = model.predict(face_for_model, verbose=0)

    # ---------- Softmax model ----------
    if pred.shape[1] == 2:
        mask_prob = float(pred[0][0])
        no_mask_prob = float(pred[0][1])

    # ---------- Sigmoid model ----------
    else:
        no_mask_prob = float(pred[0][0])
        mask_prob = 1.0 - no_mask_prob

    return mask_prob, no_mask_prob


# =========================================================
# High-Level Detection Helper
# =========================================================
def detect_mask_on_face(
    model,
    face_img,
    input_size=(224, 224),
    mask_threshold=0.5
):
    """
    End-to-end mask detection on a single face

    Returns:
        dict with:
            mask_prob
            no_mask_prob
            label
            color
    """

    face_input = preprocess_face(face_img, input_size)

    mask_prob, no_mask_prob = predict_mask(
        model,
        face_input
    )

    if mask_prob >= mask_threshold:
        label = f"Mask ({mask_prob*100:.1f}%)"
        color = (0, 255, 0)
    else:
        label = f"No Mask ({no_mask_prob*100:.1f}%)"
        color = (0, 0, 255)

    return {
        "mask_prob": mask_prob,
        "no_mask_prob": no_mask_prob,
        "label": label,
        "color": color
    }


# =========================================================
# Batch Prediction (Optional)
# =========================================================
def predict_masks_batch(model, face_list, input_size=(224, 224)):
    """
    Predict masks for multiple faces at once

    Returns:
        list of (mask_prob, no_mask_prob)
    """

    processed_faces = []

    for face in face_list:
        inp = preprocess_face(face, input_size)
        if inp is not None:
            processed_faces.append(inp[0])

    if not processed_faces:
        return []

    batch = np.array(processed_faces)

    preds = model.predict(batch, verbose=0)

    results = []

    for pred in preds:

        if len(pred) == 2:
            mask_prob = float(pred[0])
            no_mask_prob = float(pred[1])
        else:
            no_mask_prob = float(pred[0])
            mask_prob = 1.0 - no_mask_prob

        results.append((mask_prob, no_mask_prob))

    return results