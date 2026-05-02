"""
train_model.py  —  STAGE 2
============================
Reads landmark_data.csv, trains a Random Forest classifier,
evaluates accuracy, and saves the model to the Model/ folder.

Run AFTER collect_landmarks.py has built your dataset.

Install dependencies first (if not done already):
  pip install scikit-learn pandas joblib

Expected output when it finishes:
  Test accuracy: 95.xx%
  Per-class report showing precision/recall for each letter
  Model saved to   Model/asl_model.pkl
  Encoder saved to Model/label_encoder.pkl
"""

import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

# ── file paths ─────────────────────────────────────────────────────────────────
CSV_PATH   = "landmark_data.csv"
MODEL_PATH = "Model/asl_model.pkl"
ENC_PATH   = "Model/label_encoder.pkl"

# ── step 1: load the dataset ───────────────────────────────────────────────────
print("Loading data from:", CSV_PATH)
df = pd.read_csv(CSV_PATH)

# quick sanity check — print what we loaded
print(f"  Total samples: {len(df)}")
print(f"  Labels found: {sorted(df['label'].unique())}")
print(f"\n  Samples per letter:")
print(df['label'].value_counts().sort_index().to_string())
print()

# ── step 2: split into features (X) and target (y) ────────────────────────────
# X = the 63 coordinate columns (everything except 'label')
# y = the label column (the letter we want to predict)
X_raw = df.drop("label", axis=1).values
y = df["label"].values

def normalize(row):
    wx, wy, wz = row[0], row[1], row[2]
    out = []
    for i in range(0, 63, 3):
        out.extend([row[i]-wx, row[i+1]-wy, row[i+2]-wz])
    return out

import numpy as np
X = np.array([normalize(r) for r in X_raw])
# ── step 3: encode string labels to integers ──────────────────────────────────
# ML models need numbers, not strings
# LabelEncoder maps: 'A'->0, 'B'->1, 'C'->2 ... 'Z'->25
le    = LabelEncoder()
y_enc = le.fit_transform(y)
# le.classes_ stores the mapping: ['A','B',...,'Z']
# so le.classes_[0]='A', le.classes_[1]='B', etc.
print(f"Label encoding: {list(zip(le.classes_, range(26)))}\n")

# ── step 4: split data into training and testing sets ─────────────────────────
# CRITICAL: never test on data the model was trained on — that gives fake accuracy
# 80% of data goes to training, 20% goes to testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc,
    test_size    = 0.2,      # 20% held back for testing
    random_state = 42,       # fixed seed = same split every time you run
    stratify     = y_enc     # ensure each letter has equal proportion in both sets
)
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}\n")

# ── step 5: create and train the Random Forest ────────────────────────────────
print("Training Random Forest (this takes 1-3 minutes)...")
clf = RandomForestClassifier(
    n_estimators      = 300,    # build 300 decision trees — more = more stable vote
    max_depth         = None,   # let trees grow until all leaves are pure
    min_samples_split = 2,      # split a node as long as it has 2+ samples
    random_state      = 42,     # fixed seed = reproducible model
    n_jobs            = -1      # use ALL cpu cores — much faster
)

# clf.fit() is where actual training happens
# it looks at X_train (63 coords) and y_train (letter labels)
# and learns which coordinate patterns correspond to which letters
clf.fit(X_train, y_train)
print("Training complete!\n")

# ── step 6: evaluate on the test set ──────────────────────────────────────────
y_pred = clf.predict(X_test)        # predict letters for unseen test samples
acc    = accuracy_score(y_test, y_pred)
print(f"Overall test accuracy: {acc * 100:.2f}%")
print("\nPer-letter breakdown:")
print("(Look at M, N, U, V, R rows — these should be 90%+ with landmark model)")
print()
print(classification_report(
    y_test,
    y_pred,
    target_names = le.classes_   # show letter names instead of numbers
))

# ── step 7: save model and encoder to disk ────────────────────────────────────
os.makedirs("Model", exist_ok=True)    # create Model/ folder if it doesn't exist

joblib.dump(clf, MODEL_PATH)   # saves the trained Random Forest (all 200 trees)
joblib.dump(le,  ENC_PATH)     # saves the label encoder (needed to decode predictions)

print(f"Model saved to:   {MODEL_PATH}")
print(f"Encoder saved to: {ENC_PATH}")
print()

# ── tip: which letters need more data ─────────────────────────────────────────
# check the report above — any letter with f1-score below 0.90 needs more samples
# go back to collect_landmarks.py and collect more for those letters only
print("=" * 50)
print("NEXT STEP: run  python main_landmark.py")
print("=" * 50)