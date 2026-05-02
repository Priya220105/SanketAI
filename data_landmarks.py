"""
collect_landmarks.py  —  STAGE 1 (fixed)
"""

import cv2
import mediapipe as mp
import csv
import os

OUTPUT_CSV = "landmark_data.csv"
LABELS = [
    "A","B","C","D","E","F","G","H","I","J","K","L","M",
    "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"
]

mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

if not os.path.exists(OUTPUT_CSV):
    header = ["label"] + [f"{axis}{i}" for i in range(21) for axis in ["x","y","z"]]
    with open(OUTPUT_CSV, "w", newline="") as f:
        csv.writer(f).writerow(header)
    print(f"Created new file: {OUTPUT_CSV}")
else:
    print(f"Appending to existing file: {OUTPUT_CSV}")

letter_idx = 3
counter    = 0
cap        = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print(f"\n=== Landmark Collector ===")
print(f"Starting with: {LABELS[letter_idx]}")
print("S=save  |  N=next letter  |  Q=quit\n")

while True:
    success, img = cap.read()
    if not success:
        print("Camera read failed")
        break

    img     = cv2.flip(img, 1)
    h, w, _ = img.shape
    imgRGB  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    current_label = LABELS[letter_idx]
    row = None  # reset each frame

    if results.multi_hand_landmarks:
        hand_lm = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(img, hand_lm, mp_hands.HAND_CONNECTIONS)

        # build row — but DON'T save yet, wait for key press below
        row = [current_label]
        for lm in hand_lm.landmark:
            row.extend([round(lm.x, 6), round(lm.y, 6), round(lm.z, 6)])

        cv2.putText(img, "Hand detected! Press S to save", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    else:
        cv2.putText(img, "No hand detected — show your hand clearly", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    # HUD overlay
    cv2.rectangle(img, (0, 0), (w, 45), (30, 30, 30), cv2.FILLED)
    cv2.putText(img, f"Letter: {current_label}   Saved: {counter}", (10, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, "S=save  N=next  Q=quit", (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1)

    cv2.imshow("Landmark Collector — SanketAI", img)

    # ── ONE waitKey at the bottom — reads ALL keys reliably ──────────────────
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        if row is not None:   # only save if hand was detected this frame
            with open(OUTPUT_CSV, "a", newline="") as f:
                csv.writer(f).writerow(row)
            counter += 1
            print(f"  [{current_label}] sample #{counter} saved")
        else:
            print("  No hand detected — can't save!")

    elif key == ord('n'):
        print(f"\n  Done with [{current_label}] — {counter} samples")
        letter_idx = (letter_idx + 1) % len(LABELS)
        counter    = 0
        print(f"  Now collecting: [{LABELS[letter_idx]}]\n")

    elif key in [ord('q'), 27]:
        print("\nQuitting...")
        break

cap.release()
cv2.destroyAllWindows()
print(f"\nDone! Data saved to: {OUTPUT_CSV}")
print(f"Next step: run  python train_model.py")