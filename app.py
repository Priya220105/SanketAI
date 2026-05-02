"""
app.py — SanketAI Flask Web App
================================
Run with: python app.py
Open browser at: http://localhost:5000
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import numpy as np
import joblib
import os
from collections import deque

app = Flask(__name__)

# ── load model ─────────────────────────────────────────────────────────────────
clf = joblib.load("Model/asl_model.pkl")
le  = joblib.load("Model/label_encoder.pkl")
print("Model loaded!")

# ── mediapipe ──────────────────────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ── shared state ───────────────────────────────────────────────────────────────
state = {
    "letter":     "",
    "confidence": 0,
    "sentence":   "",
    "buffer":     [],
}
pred_history = deque(maxlen=7)
BUFFER_THRESHOLD = 15
CONFIDENCE_MIN   = 0.60

def normalize(hand_lm):
    wrist = hand_lm.landmark[0]
    row = []
    for lm in hand_lm.landmark:
        row.extend([lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z])
    return row

def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, img = cap.read()
        if not success:
            break

        img    = cv2.flip(img, 1)
        h, w, _ = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            hand_lm = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(img, hand_lm, mp_hands.HAND_CONNECTIONS)

            # normalize + predict
            row      = normalize(hand_lm)
            features = np.array(row).reshape(1, -1)
            proba    = clf.predict_proba(features)[0]
            pred_history.append(proba)
            avg_proba      = np.mean(pred_history, axis=0)
            top_idx        = np.argmax(avg_proba)
            confidence_val = float(avg_proba[top_idx])
            detected_letter = le.classes_[top_idx]

            state["letter"]     = detected_letter
            state["confidence"] = round(confidence_val * 100)

            # buffer logic
            if confidence_val >= CONFIDENCE_MIN:
                state["buffer"].append(detected_letter)
            else:
                state["buffer"] = []

            if len(state["buffer"]) >= BUFFER_THRESHOLD:
                most_common = max(set(state["buffer"]), key=state["buffer"].count)
                state["sentence"] += most_common
                state["buffer"] = []

            # draw on frame
            x_list = [int(lm.x * w) for lm in hand_lm.landmark]
            y_list = [int(lm.y * h) for lm in hand_lm.landmark]
            x_min  = max(0, min(x_list) - 20)
            x_max  = min(w, max(x_list) + 20)
            y_min  = max(0, min(y_list) - 20)
            y_max  = min(h, max(y_list) + 20)

            color = (0,255,0) if confidence_val>=0.75 else (0,165,255) if confidence_val>=0.5 else (0,0,255)
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, 3)

            label = detected_letter if confidence_val >= CONFIDENCE_MIN else "?"
            cv2.rectangle(img, (x_min, y_min-50), (x_min+110, y_min), (255,0,255), cv2.FILLED)
            cv2.putText(img, label, (x_min+5, y_min-12),
                        cv2.FONT_HERSHEY_COMPLEX, 1.5, (255,255,255), 2)
            cv2.putText(img, f"{state['confidence']}%", (x_min+68, y_min-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220,220,220), 1)
        else:
            state["letter"]     = ""
            state["confidence"] = 0

        # encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# ── routes ─────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/state')
def get_state():
    return jsonify({
        "letter":     state["letter"],
        "confidence": state["confidence"],
        "sentence":   state["sentence"]
    })

@app.route('/clear', methods=['POST'])
def clear():
    state["sentence"] = ""
    state["buffer"]   = []
    return jsonify({"ok": True})

@app.route('/backspace', methods=['POST'])
def backspace():
    state["sentence"] = state["sentence"][:-1]
    return jsonify({"sentence": state["sentence"]})

@app.route('/space', methods=['POST'])
def space():
    state["sentence"] += " "
    return jsonify({"sentence": state["sentence"]})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)