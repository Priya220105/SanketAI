"""
main_landmark.py  —  STAGE 3
==============================
Real-time ASL recognition using MediaPipe landmarks + Random Forest.

Run AFTER train_model.py has saved the model files.

Controls:
  SPACE = speak the current sentence (text-to-speech)
  C     = clear the sentence
  ESC   = quit

Color coding of the bounding box:
  GREEN  = high confidence (>75%) — letter is being confirmed
  ORANGE = medium confidence (50-75%) — uncertain, keep holding
  RED    = low confidence (<50%) — shows ? instead of a letter
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'   # suppress any tensorflow warnings

import cv2
import mediapipe as mp
import numpy as np
import joblib
import time
import pyttsx3

# ── load the trained model and label encoder ──────────────────────────────────
print("Loading model...")
clf = joblib.load("../Model/asl_model.pkl")      # the Random Forest (200 trees)
le  = joblib.load("../Model/label_encoder.pkl")  # maps 0->'A', 1->'B', etc.
print(f"Model loaded. Recognises: {list(le.classes_)}\n")

# ── text-to-speech setup ──────────────────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty('rate', 150)   # speaking speed (words per minute)

# ── mediapipe setup ────────────────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ── state variables ────────────────────────────────────────────────────────────
sentence         = ""    # accumulates confirmed letters: '' -> 'H' -> 'HE' -> 'HEY'
letter_buffer    = []    # stores last N predictions before confirming
BUFFER_THRESHOLD = 15    # how many consistent frames needed to confirm a letter
                         # 20 frames @ ~30 FPS = about 0.6 seconds
CONFIDENCE_MIN   = 0.60   # minimum probability to trust — below this shows '?'
pTime            = 0     # for FPS calculation

cap = cv2.VideoCapture(0)
print("=== SanketAI — Running ===")
print("Show letters to the camera")
print("SPACE=speak  C=clear  ESC=quit\n")

# ── main loop ──────────────────────────────────────────────────────────────────
while True:
    success, img = cap.read()
    if not success:
        break

    img       = cv2.flip(img, 1)          # mirror horizontally
    imgOutput = img.copy()                # keep a clean copy to draw on
    h, w, _   = img.shape

    imgRGB  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    detected_letter = None
    confidence_val  = 0.0
    from collections import deque
    if 'pred_history' not in dir():
        pred_history = deque(maxlen=7)  # stores last 7 frame predictions
    if results.multi_hand_landmarks:
        hand_lm = results.multi_hand_landmarks[0]

        # ── extract 63 landmark features ──────────────────────────────────────
        # MUST be in the same order as collect_landmarks.py
        row = []
        wrist = hand_lm.landmark[0]
        for lm in hand_lm.landmark:
            row.extend([lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z])
        # reshape to (1, 63) — model expects (n_samples, n_features)
        features = np.array(row).reshape(1, -1)

        # ── predict using Random Forest ───────────────────────────────────────
        # predict_proba returns probability for all 26 letters
        # e.g. [0.01, 0.02, ..., 0.89, ..., 0.01]  — index with highest = prediction
        proba = clf.predict_proba(features)[0]
        pred_history.append(proba)

        # average probabilities across last 7 frames — smooths flickering
        avg_proba      = np.mean(pred_history, axis=0)
        top_idx        = np.argmax(avg_proba)
        confidence_val = avg_proba[top_idx]
        detected_letter = le.classes_[top_idx]

        # ── temporal buffer: stability system ────────────────────────────────
        if confidence_val >= CONFIDENCE_MIN:
            letter_buffer.append(detected_letter)  # confident — add to buffer
        else:
            letter_buffer = []                      # not confident — reset buffer

        if len(letter_buffer) >= BUFFER_THRESHOLD:
            # find the letter that appeared most often in the last 20 frames
            most_common = max(set(letter_buffer), key=letter_buffer.count)

            # only add if it's different from the last confirmed letter
            # prevents 'AAAA' when holding A — gives just 'A'
            if not sentence or most_common != sentence[-1]:
                sentence += most_common

            letter_buffer = []   # reset and start fresh

        # ── bounding box coordinates ──────────────────────────────────────────
        x_list = [int(lm.x * w) for lm in hand_lm.landmark]
        y_list = [int(lm.y * h) for lm in hand_lm.landmark]
        x_min  = max(0, min(x_list) - 20)
        x_max  = min(w, max(x_list) + 20)
        y_min  = max(0, min(y_list) - 20)
        y_max  = min(h, max(y_list) + 20)

        # ── color of box based on confidence ─────────────────────────────────
        if confidence_val >= 0.75:
            box_color = (0, 255, 0)     # GREEN  — high confidence
        elif confidence_val >= 0.50:
            box_color = (0, 165, 255)   # ORANGE — medium confidence
        else:
            box_color = (0, 0, 255)     # RED    — low confidence

        # draw bounding box around the hand
        cv2.rectangle(imgOutput, (x_min, y_min), (x_max, y_max), box_color, 3)

        # ── label display above the box ───────────────────────────────────────
        # show '?' if not confident enough — honest feedback to the user
        label_text = detected_letter if confidence_val >= CONFIDENCE_MIN else "?"
        conf_pct   = f"{confidence_val * 100:.0f}%"

        cv2.rectangle(imgOutput, (x_min, y_min - 50), (x_min + 110, y_min),
                      (255, 0, 255), cv2.FILLED)
        cv2.putText(imgOutput, label_text, (x_min + 5, y_min - 12),
                    cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 2)
        cv2.putText(imgOutput, conf_pct, (x_min + 68, y_min - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)

        # draw the 21 landmark dots and connections
        mp_drawing.draw_landmarks(imgOutput, hand_lm, mp_hands.HAND_CONNECTIONS)

    # ── sentence bar at the bottom of the screen ──────────────────────────────
    cv2.rectangle(imgOutput, (0, h - 60), (w, h), (30, 30, 30), cv2.FILLED)
    cv2.putText(imgOutput, f"Sentence: {sentence}", (10, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # ── controls hint at the top ──────────────────────────────────────────────
    cv2.putText(imgOutput, "SPACE=speak  C=clear  ESC=quit", (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

    # ── FPS display ───────────────────────────────────────────────────────────
    cTime = time.time()
    fps   = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(imgOutput, f"FPS: {int(fps)}", (w - 110, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

    cv2.imshow("SanketAI", imgOutput)

    # ── key handling ──────────────────────────────────────────────────────────
    key = cv2.waitKey(1) & 0xFF   # & 0xFF masks to 8 bits for cross-platform safety

    if key == 27:                           # ESC
        print("Exiting...")
        break
    elif key == ord('c'):                   # C = clear sentence
        sentence = ""
        print("Sentence cleared")
    elif key == ord(' ') and sentence:      # SPACE = speak sentence
        print(f"Speaking: '{sentence}'")
        engine.say(sentence)
        engine.runAndWait()

# ── cleanup ───────────────────────────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
print("Done.")