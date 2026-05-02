# ── IMPORTS ────────────────────────────────────────────────────────
import cv2
# cv2 = OpenCV. Used for: opening camera, showing windows, drawing text on frames
# Without this: no camera, no display

import mediapipe as mp
# mediapipe = Google's hand detection library
# It finds your hand and gives you 21 points (landmarks) with x,y,z coordinates
# Without this: no hand detection at all

import csv
# csv = Python's built-in module for reading/writing CSV files
# We use it to save each hand pose as one row in landmark_data.csv

import os
# os = operating system module. We use it to check if the CSV file already exists
# so we don't overwrite old data when restarting the script

# ── SETTINGS ───────────────────────────────────────────────────────
OUTPUT_CSV = "landmark_data.csv"
# This is the file where ALL collected data is stored
# Each row = one hand pose with 63 coordinate values + 1 label (the letter)

import string
LABELS = list(string.ascii_uppercase)  # ['A','B','C',...,'Z']
# The 26 ASL letters. The index position matters — letter_idx 0 = A, 1 = B, etc.
# When you press N to go to the next letter, letter_idx increases by 1

# ── MEDIAPIPE SETUP ─────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
# mp.solutions.hands is the hand tracking module inside mediapipe
# This line just gets a reference to it — no detection happens yet

mp_drawing = mp.solutions.drawing_utils
# mp_drawing lets us draw the skeleton (dots + lines) on the video frame
# Optional but useful to visually confirm the hand is being tracked correctly

hands = mp_hands.Hands(
    static_image_mode  = False,
    # False = treat input as a VIDEO (uses tracking between frames = faster)
    # True  = treat each frame as a new IMAGE (slower, redetects every frame)

    max_num_hands = 1,
    # We only want to track ONE hand. More hands = slower + complicates the model

    min_detection_confidence = 0.7,
    # How confident mediapipe must be to say 'yes, there is a hand here'
    # 0.7 = 70%. Below this confidence it will NOT report a hand.
    # Too low (e.g. 0.3) = lots of false detections on non-hand objects
    # Too high (e.g. 0.95) = misses hand when partially occluded

    min_tracking_confidence = 0.7
    # Once a hand is found, how confident it must be to KEEP tracking it
    # vs redetecting from scratch. 0.7 is a good balance of speed and stability
)

# ── CREATE CSV FILE IF IT DOESN'T EXIST ─────────────────────────────
if not os.path.exists(OUTPUT_CSV):
    # Check if the file already exists BEFORE creating it
    # This matters: if you run the script twice, you DON'T want to
    # overwrite your previous data. Only create if missing.

    header = ["label"] + [f"{axis}{i}" for i in range(21) for axis in ["x","y","z"]]
    # Build the header row: label, x0, y0, z0, x1, y1, z1 ... x20, y20, z20
    # range(21) = 0 to 20 (the 21 landmark points)
    # for each point we have x, y, z — so 21 x 3 = 63 coordinate columns
    # Plus 1 label column = 64 columns total in the CSV

    with open(OUTPUT_CSV, "w", newline="") as f:
    # 'w' mode = write (creates new file). newline='' is required for csv on Windows
        csv.writer(f).writerow(header)
    # Write the header row. This is the first line of the CSV.
    # Example first line: label,x0,y0,z0,x1,y1,z1,...,x20,y20,z20

cap = cv2.VideoCapture(0)
letter_idx = 0
current_label = LABELS[letter_idx]
while True:  # Run forever until user presses Q
    success, img = cap.read()
    # cap.read() grabs one frame from the webcam
    # success = True if frame was captured successfully
    # img     = the actual frame as a numpy array of shape (height, width, 3)
    # The 3 channels are Blue, Green, Red (OpenCV uses BGR not RGB)

    img     = cv2.flip(img, 1)
    # Flip horizontally (mirror effect) so it feels natural
    # Without this: raising your RIGHT hand shows up on LEFT side of screen

    imgRGB  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # MediaPipe expects RGB (Red,Green,Blue) but OpenCV gives BGR
    # This converts the color order. Skipping this = wrong colors = bad detection

    results = hands.process(imgRGB)
    # THIS is where MediaPipe does its work.
    # It runs its neural network on imgRGB and returns:
    #   results.multi_hand_landmarks = list of detected hands
    #   Each hand has 21 landmarks, each landmark has .x .y .z
    #   If NO hand found: results.multi_hand_landmarks = None
    #rendering 
    if results.multi_hand_landmarks:
    # Only enter this block if at least one hand was detected

        hand_lm = results.multi_hand_landmarks[0]
        # Take the FIRST detected hand (index 0)
        # hand_lm.landmark is a list of 21 objects, each with .x .y .z
        row = [current_label]
        # Start building the CSV row. First value = the letter label (e.g. 'A')

        for lm in hand_lm.landmark:
        # Loop through all 21 landmark points one by one
            row.extend([round(lm.x,6), round(lm.y,6), round(lm.z,6)])
            # .x = horizontal position (0.0 = left edge, 1.0 = right edge of frame)
            # .y = vertical position   (0.0 = top,       1.0 = bottom of frame)
            # .z = depth               (negative = closer to camera than wrist)
            # round(..., 6) = keep 6 decimal places. Enough precision, not too large
            # extend() adds all three values to the row list

        # After the loop: row = ['A', x0, y0, z0, x1, y1, z1, ..., x20, y20, z20]
        # That is 1 + 63 = 64 values. One row in the CSV.
        key = cv2.waitKey(1) & 0xFF
        # Wait 1ms for a key press. & 0xFF gets just the last 8 bits (the char code)

        if key == ord('s'):
        # ord('s') = ASCII code of the letter s
        # If S was pressed: save the current row to the CSV

            with open(OUTPUT_CSV, "a", newline="") as f:
            # 'a' mode = APPEND (add to end of file, don't overwrite)
            # This is how we keep adding rows without losing previous data
                csv.writer(f).writerow(row)
            # Write the 64-value row to the CSV file
            # One row = one training sample for one letter
