import json
import os
import numpy as np
from PIL import Image
import streamlit as st
import tensorflow as tf

st.set_page_config(
    page_title="Indian Sign Language Gesture Recognition",
    page_icon="🤟",
    layout="centered",
)

# Folder where model and class_labels.json are located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KERAS_PATH = os.path.join(BASE_DIR, "isl_sign_language_cnn_fast.keras")
H5_PATH = os.path.join(BASE_DIR, "isl_sign_language_cnn_fast.h5")
LABELS_PATH = os.path.join(BASE_DIR, "class_labels.json")

IMG_SIZE = (64, 64)


@st.cache_resource
def load_labels_and_model():
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        index_to_class = json.load(f)

    num_classes = len(index_to_class)

    # 1. Try loading .keras model
    if os.path.exists(KERAS_PATH):
        try:
            model = tf.keras.models.load_model(KERAS_PATH, compile=False)
            return model, index_to_class
        except Exception:
            pass

    # 2. Try loading .h5 model directly
    if os.path.exists(H5_PATH):
        try:
            model = tf.keras.models.load_model(H5_PATH, compile=False)
            return model, index_to_class
        except Exception:
            # 3. Rebuild architecture and load weights from .h5
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(64, 64, 3)),
                tf.keras.layers.Conv2D(16, (3, 3), activation="relu", padding="same"),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(num_classes, activation="softmax"),
            ])
            model.load_weights(H5_PATH)
            return model, index_to_class

    raise FileNotFoundError("Model file (.keras or .h5) not found.")


st.title("🤟 Indian Sign Language Gesture Recognition")
st.write("Upload a sign language hand gesture image to predict the sign.")

try:
    model, index_to_class = load_labels_and_model()
except Exception as e:
    st.error(f"Error loading model or labels: {e}")
    st.stop()

uploaded_file = st.file_uploader(
    "Choose an image...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("Predicting gesture..."):
        resized_img = image.resize(IMG_SIZE)
        img_array = np.array(resized_img).astype("float32") / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        preds = model.predict(img_array, verbose=0)[0]
        pred_index = int(np.argmax(preds))
        confidence = float(np.max(preds))
        predicted_class = index_to_class.get(str(pred_index), f"Class {pred_index}")

    st.success(f"**Predicted Gesture:** {predicted_class}")
    st.info(f"**Confidence:** {confidence * 100:.2f}%")

    st.subheader("Top 5 Predictions")
    top5_indices = np.argsort(preds)[::-1][:5]
    for idx in top5_indices:
        label = index_to_class.get(str(int(idx)), f"Class {int(idx)}")
        score = float(preds[idx])
        st.write(f"**{label}** — {score * 100:.2f}%")
        st.progress(min(max(score, 0.0), 1.0))
