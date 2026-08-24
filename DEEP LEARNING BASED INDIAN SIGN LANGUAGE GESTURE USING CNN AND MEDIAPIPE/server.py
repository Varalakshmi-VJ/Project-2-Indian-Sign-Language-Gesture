from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import json
import os
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# ── Load model and class labels once at startup ──
MODEL_PATH = "isl_sign_language_cnn_fast.keras"  # or .h5
LABELS_PATH = "class_labels.json"

print("Loading model...")

# Try .keras first, then .h5, then rebuild architecture
try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("Model loaded from .keras!")
except Exception as e:
    print(f".keras failed: {e}")
    try:
        model = tf.keras.models.load_model(
            "isl_sign_language_cnn_fast.h5", compile=False
        )
        print("Model loaded from .h5!")
    except Exception as e2:
        print(f".h5 direct load failed: {e2}, rebuilding architecture...")
        with open(LABELS_PATH, "r") as lf:
            _labels = json.load(lf)
        num_classes = len(_labels)
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(64, 64, 3)),
            tf.keras.layers.Conv2D(16, (3,3), activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D((2,2)),
            tf.keras.layers.Conv2D(32, (3,3), activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D((2,2)),
            tf.keras.layers.Conv2D(64, (3,3), activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D((2,2)),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(num_classes, activation="softmax")
        ])
        model.load_weights("isl_sign_language_cnn_fast.h5")
        print("Weights loaded into rebuilt model!")

with open(LABELS_PATH, "r") as f:
    index_to_class = json.load(f)

IMG_SIZE = (64, 64)

@app.route("/")
def home():
    return "ISL Sign Language API is running!"

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Read and preprocess image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img = img.resize(IMG_SIZE)

        img_array = np.array(img).astype("float32") / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Run prediction
        preds = model.predict(img_array)
        pred_index = int(np.argmax(preds[0]))
        confidence = float(np.max(preds[0]))
        predicted_class = index_to_class[str(pred_index)]

        # Top 5 predictions
        top5_indices = np.argsort(preds[0])[::-1][:5]
        top5 = [
            {
                "label": index_to_class[str(int(i))],
                "score": float(preds[0][i])
            }
            for i in top5_indices
        ]

        return jsonify({
            "predicted": predicted_class,
            "confidence": confidence,
            "top5": top5
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)