# SanketAI — Design Document
## AI-Powered Sign Language Learning Platform
### AI for Bharat Hackathon | Track: AI for Learning & Developer Productivity

---

## 1. System Overview

SanketAI is a webcam-based, AI-powered sign language learning platform built for deaf and hard-of-hearing learners in India. Unlike conventional sign language apps that only detect signs, SanketAI functions as a **learning companion** — it teaches, corrects, and adapts.

The platform is designed around four core design principles extracted directly from the product vision:

1. **Hands-on learning** instead of passive video watching
2. **No special hardware** — works on basic laptops or tablets with a standard webcam
3. **Offline-first and low-bandwidth friendly** for rural and underserved regions across Bharat
4. **Beginner to advanced learning flow** with continuous practice and intelligent feedback

---

## 2. High-Level Architecture

The system follows a **three-layer architecture**: Client/Edge (on device), AI Core (on device), and Cloud (optional and asynchronous). This structure ensures the platform works fully offline while optionally leveraging cloud services for multilingual feedback and progress sync.

```
┌──────────────────────────────────────────────────────┐
│              CLIENT / EDGE  (On Device)               │
│                                                      │
│   User Device          Webcam Input      Edge Processing
│   (Web / Mobile)       Live Hand Capture             │
│                                                      │
│   • Browser-based UI   • 30fps video     • MediaPipe hand detection
│   • Split-screen view  • Real-time       • Landmark extraction (21 pts/hand)
│   • Reference signs    • No upload       • Normalization (scale + rotation)
│   • Feedback display                     • Lightweight preprocessing
│                                                      │
└──────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────┐
│                  AI CORE  (On Device)                 │
│                                                      │
│   AI Gesture Recognition Model      Learning Feedback Engine
│                                                      │
│   • Prototyped: Google Teachable    • Detects incorrect hand shape,
│     Machine                           orientation, timing
│   • Fine-tuned on ISL dataset       • Generates corrective guidance
│   • Optimized for Indian Sign       • Updates accuracy & level progression
│     Language                        • Feedback delivered in user's
│   • Runs locally for real-time        preferred language
│     inference (<500ms)              • Correct → progress updated, level unlocked
│                                     • Incorrect → visual + text correction tips
│                                                      │
└──────────────────────────────────────────────────────┘
                            │
                  (Optional Sync — when online)
                            │
                            ▼
┌──────────────────────────────────────────────────────┐
│           CLOUD  (Optional & Asynchronous)            │
│                                                      │
│   Amazon S3                        AWS Bedrock        │
│                                                      │
│   • Anonymized progress &          • Multilingual feedback generation
│     usage data                     • Hindi, English, regional languages
│   • Encrypted JSON storage         • Generates corrective explanations
│   • Sync only when online          • Called asynchronously when available
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Key architectural decision:** The cloud layer is marked **"Optional & Asynchronous"** deliberately. Core sign recognition, corrective feedback logic, and learning progression all run entirely on the user's device. Cloud services enhance the experience (multilingual feedback via Bedrock, progress backup via S3) but are never required. This is what makes SanketAI viable for rural Bharat where 60% of users lack reliable 4G.

---

## 3. Process Flow / Data Flow

The following describes the complete user journey from opening a lesson to receiving feedback, matching the process flow defined in the product design:

```
Step 1: USER OPENS LEARNING SESSION
        └── Selects lesson and target sign (alphabet, word, or phrase)
        └── Reference sign displayed on screen

Step 2: WEBCAM CAPTURES HAND GESTURE
        └── Live practice input at 30fps
        └── No video data is stored or uploaded

Step 3: PREPROCESSING (On-Device)
        └── MediaPipe Holistic extracts 21 hand landmarks per frame
        └── Landmarks normalized for scale and rotation invariance
        └── Lightweight preprocessing optimized for real-time use

Step 4: SIGN RECOGNITION MODEL (Edge AI)
        └── Model (prototyped via Google Teachable Machine, fine-tuned on ISL) runs inference
        └── Input: sequence of 21 hand landmarks × 30 frames
        └── Output: predicted sign class + confidence score
        └── Inference latency: < 500ms on mid-range device
        └── Runs entirely on user's device — no cloud call required

Step 5: ACCURACY CALCULATION
        └── System compares learner's predicted sign against target sign
        └── Calculates accuracy score
        └── Determines error type if prediction doesn't match

Step 6A: CORRECT SIGN (Accuracy ≥ threshold)
        └── Progress updated (attempts, accuracy logged)
        └── Level advancement checked
        └── Next sign or level loaded

Step 6B: INCORRECT SIGN (Accuracy < threshold)
        └── Error type identified: hand shape / orientation / movement timing
        └── Visual correction overlay shown on screen
        └── Text correction tips generated
        └── AWS Bedrock translates feedback into user's preferred language
            (Hindi, English, or regional language) — if online
        └── Learner retries the sign

Step 7: PROGRESS TRACKING
        └── Accuracy trends, attempts, and learning history saved locally (IndexedDB)
        └── Level completion and progression tracked
        └── When online: anonymized progress syncs asynchronously to Amazon S3
```

---

## 4. Component Design

### 4.1 User Interface (Frontend)

| Component | Description |
|---|---|
| **Landing / Login Screen** | Simple entry point. No account required for basic use. Optional sign-in for progress sync. |
| **Lesson Selector** | Browse 50+ ISL signs organized by level (Beginner / Intermediate / Advanced) and scenario (School, Home, Emotions). |
| **Split-Screen Practice View** | Left panel: reference sign (video or illustration). Right panel: live webcam feed with hand landmark overlay. Core learning interface. |
| **Feedback Overlay** | After each attempt, displays accuracy score, error type (if incorrect), and corrective tips. Color-coded: green for correct, red for incorrect with specific guidance. |
| **Progress Dashboard** | Accuracy graphs over time, level completion badges, signs mastered count. Exportable as PDF. |
| **Family Mode Screen** | Shared session view for parent + child. Shows both users' attempts. Prioritizes survival signs. |
| **Teacher Dashboard** | Multi-student view showing progress, accuracy trends, and flagged students needing support. Sharable via WhatsApp. |

**Design principle:** The UI is optimized for children (ages 8+) and non-technical users. Large buttons, clear visual cues, and minimal text input required.

---

### 4.2 Hand Tracking Module (MediaPipe)

| Attribute | Detail |
|---|---|
| **Library** | MediaPipe Holistic |
| **Output** | 21 landmarks per hand (x, y, z coordinates) |
| **Processing** | Runs entirely on-device in the browser |
| **Normalization** | Landmarks are normalized for scale (user distance from camera) and rotation (hand orientation) to ensure consistent detection regardless of device placement |
| **Performance** | Lightweight preprocessing designed for real-time use on low-end devices |

MediaPipe is the correct choice here because it runs in-browser via WebAssembly, requires no server, and works on devices as low-end as ₹5,000 government-issued tablets.

---

### 4.3 AI Gesture Recognition Model

| Attribute | Detail |
|---|---|
| **Prototyping Tool** | Google Teachable Machine |
| **Fine-tuning** | Custom fine-tuning on Indian Sign Language (ISL) dataset |
| **Optimization** | Optimized specifically for ISL — not generic ASL or international sign |
| **Input** | Sequence of 21 hand landmarks × 30 frames (captures temporal motion, not just a single pose) |
| **Output** | Predicted sign class (50+ classes) + confidence score |
| **Inference Engine** | TensorFlow.js — runs natively in the browser |
| **Inference Latency** | < 500ms on a mid-range laptop or tablet |
| **Accuracy Target** | 90%+ on ISL test set |
| **Deployment** | Runs entirely on user's device (Edge AI) — no cloud dependency |

**Why Google Teachable Machine + fine-tuning:** Teachable Machine provides rapid prototyping capability and generates TensorFlow.js-compatible models out of the box. Fine-tuning on a dedicated ISL dataset brings accuracy to production-ready levels while keeping the development cycle fast — critical for a hackathon timeline.

---

### 4.4 Learning Feedback Engine

This is the **core AI innovation** of SanketAI — the component that separates it from simple sign detection tools.

```
FEEDBACK LOGIC:

  Prediction matches target sign?
  │
  ├── YES (Accuracy ≥ 80%)
  │   └── "Correct!" → Progress updated, level advancement checked
  │
  └── NO
      └── Error Classification:
          ├── Hand Shape Error    → "Your fingers are positioned incorrectly.
          │                          Try spreading them wider."
          ├── Orientation Error   → "Your palm should face toward the camera.
          │                          Rotate your hand slightly."
          └── Timing Error        → "Hold the sign for 2 seconds before releasing.
                                     Try again more slowly."
      └── Correction Tips:
          ├── Visual overlay on webcam feed highlighting correct position
          └── Text explanation of the specific error
      └── Multilingual Delivery:
          └── AWS Bedrock translates the correction into user's preferred language
              (Hindi, English, or regional language) — when online
              └── Fallback: English feedback displayed offline
```

**Key design decisions:**
- Feedback is **explainable** — never just "Wrong." Always specifies what went wrong and how to fix it.
- Three specific error categories (hand shape, orientation, timing) match how ISL is actually taught by human instructors.
- Multilingual output via AWS Bedrock ensures non-English speaking parents (80% of deaf children have hearing parents) can understand the feedback.

---

### 4.5 Adaptive Learning System

| Level | Signs | Description |
|---|---|---|
| **Beginner** | Signs 1–20 | Basic alphabet signs and essential survival signs (e.g., "Hello", "Thank you", "Help", "I love you"). Slow pace, generous accuracy thresholds. |
| **Intermediate** | Signs 21–40 | Common words and short phrases used in daily life. Accuracy thresholds tighten. Timed practice introduced. |
| **Advanced** | Signs 41–50+ | Contextual and conversational signs. Scenario-based modules (School, Home, Emotions). Highest accuracy required for progression. |

**Progression logic:**
- System tracks accuracy across multiple attempts per sign.
- Level advancement is automatic — triggered when learner achieves consistent accuracy (80%+) across all signs in current level.
- If accuracy drops, system re-introduces previously mastered signs for revision (spaced repetition principle).

---

### 4.6 Offline & Cloud Sync

```
LOCAL (Always Active)
├── Sign Recognition         → TensorFlow.js model runs in browser
├── Hand Tracking            → MediaPipe runs in browser
├── Feedback Engine          → Logic runs client-side
├── Progress Storage         → IndexedDB (browser-native, no install needed)
└── Lesson Content           → Pre-loaded sign library bundled with app

CLOUD (Optional — fires only when online)
├── Amazon S3
│   ├── Stores: Anonymized progress data (encrypted JSON)
│   ├── Stores: Aggregated usage analytics (no PII)
│   └── Sync: Asynchronous — queues locally, uploads when connectivity detected
│
└── AWS Bedrock
    ├── Purpose: Multilingual feedback generation
    ├── Input: Error type + sign name + target language
    ├── Output: Corrective feedback in Hindi / English / regional language
    └── Fallback: If offline, English feedback generated locally
```

**Privacy architecture:**
- No video frames are ever stored or transmitted.
- No facial images or biometric identifiers are retained.
- Progress data is anonymized before any cloud sync.
- All AI processing happens on the user's device first.

---

## 5. Database Design

### 5.1 Local Storage (IndexedDB)

```
Database: sanketai_local

Object Stores:
├── user_profile
│   ├── preferred_language: "hindi" | "english" | "tamil" | ...
│   ├── current_level: 1 | 2 | 3
│   └── display_name: string (optional)
│
├── progress
│   ├── sign_id: string
│   ├── attempts: number
│   ├── best_accuracy: float (0–1)
│   ├── average_accuracy: float (0–1)
│   ├── mastered: boolean
│   ├── last_practiced: timestamp
│   └── error_history: [{type, timestamp}]
│
├── lessons
│   ├── lesson_id: string
│   ├── level: 1 | 2 | 3
│   ├── scenario: "school" | "home" | "emotions"
│   ├── signs: [sign_id, ...]
│   ├── completed: boolean
│   └── completion_date: timestamp
│
└── sync_queue
    ├── event_type: "progress_update" | "level_complete"
    ├── payload: JSON (anonymized)
    ├── created_at: timestamp
    └── synced: boolean
```

### 5.2 Cloud Storage (Amazon S3)

```
Bucket: sanketai-progress-data

Structure:
├── progress/
│   └── {anonymized_user_id}/
│       └── {date}.json          ← Daily progress snapshots (anonymized)
│
└── analytics/
    └── aggregated/
        └── {date}.json          ← Platform-wide aggregated metrics (no PII)
```

---

## 6. AWS Integration Design

### 6.1 Amazon S3 — Progress Sync

| Attribute | Detail |
|---|---|
| **Purpose** | Backup anonymized learner progress; enable cross-device continuity |
| **Trigger** | Asynchronous — fires when app detects internet connectivity |
| **Data** | Anonymized progress JSON (no name, email, or device identifiers) |
| **Encryption** | Server-side encryption (SSE-S3) |
| **Frequency** | Once per session when online; queued locally when offline |

### 6.2 AWS Bedrock — Multilingual Feedback

| Attribute | Detail |
|---|---|
| **Purpose** | Generate corrective feedback in the learner's preferred language |
| **Input** | Error type (hand shape / orientation / timing) + sign name + target language |
| **Output** | Natural language correction in Hindi, English, or regional language |
| **Trigger** | Called when an incorrect sign is detected and user is online |
| **Fallback** | If offline, English-language feedback is generated locally using pre-defined templates |
| **Latency** | Asynchronous — does not block the core feedback loop |

**Why Bedrock is the right fit:** 80% of deaf children in India have hearing parents who are non-English speakers. Bedrock enables feedback in the parent's native language without maintaining a manual translation database for every correction message and every language. It scales naturally as new regional languages are added.

---

## 7. Security & Privacy

| Principle | Implementation |
|---|---|
| **No video storage** | Webcam frames are processed in real-time and never saved to disk or transmitted |
| **No biometric data** | No facial images, voice recordings, or other biometric identifiers are captured or retained |
| **No PII in cloud** | All data synced to S3 is fully anonymized before transmission |
| **Consent-based** | Users explicitly opt-in to cloud sync; core functionality works without it |
| **Transparent AI** | Feedback always explains why a sign was marked incorrect — no black-box decisions |
| **Local-first** | All AI processing (hand tracking, sign recognition, feedback logic) happens on the user's device |

---

## 8. Scalability Design

| Challenge | Solution |
|---|---|
| Serving 10,000+ concurrent learners | Edge-first architecture — each user's device runs its own AI inference. No shared GPU or server bottleneck. |
| Zero marginal cost per user | Model runs in-browser via TensorFlow.js. No per-request cloud inference cost for core functionality. |
| Expanding to new languages | AWS Bedrock handles language generation — adding a new regional language requires only updating the language preference option, not retraining any model. |
| Deploying across NGOs and schools | No installation required — runs in any modern browser. One shared tablet can serve multiple students sequentially. |
| Growing sign vocabulary | Adding new signs requires only new training samples and model fine-tuning — the entire platform architecture remains unchanged. |

---

## 9. Testing Strategy

| Test Type | What to Test | Method |
|---|---|---|
| **Unit Tests** | MediaPipe landmark extraction, accuracy calculation logic, feedback classification | Jest (JavaScript) |
| **Model Tests** | Sign recognition accuracy across 50+ signs | Test dataset (held-out 20% from training) — target 90%+ |
| **Integration Tests** | End-to-end flow: webcam → landmarks → prediction → feedback → progress update | Selenium / Playwright |
| **Performance Tests** | Inference latency on target devices (mid-range laptop, ₹5,000 tablet) | Target: < 500ms |
| **Offline Tests** | Full practice session with no internet connection | Manual + automated |
| **Usability Tests** | Children (ages 8–12) and non-technical adults can complete a lesson without guidance | User testing with target demographic |

---

## 10. Deployment Plan

| Item | Detail |
|---|---|
| **Hosting** | Vercel (free tier) — static web app deployment |
| **App Type** | Progressive Web App (PWA) — installable on desktop and mobile, works offline |
| **Model Hosting** | TensorFlow.js model bundled with the app (no separate model server) |
| **CDN** | Static assets (JS, CSS, model weights) served via Vercel CDN |
| **Cloud Services** | AWS Bedrock + S3 — configured via AWS Console, invoked via SDK |
| **CI/CD** | GitHub → Vercel auto-deploy on push to main branch |

---

## 11. Design Rationale

| Decision | Why |
|---|---|
| Edge AI over cloud inference | Enables offline use, eliminates latency, reduces cost, works on rural 2G/3G |
| Google Teachable Machine + fine-tuning | Rapid prototyping with production-quality TensorFlow.js output; fine-tuning on ISL dataset brings accuracy to 90%+ |
| MediaPipe over custom hand detection | Battle-tested, runs in browser, handles lighting/angle variations, 21 landmarks provide rich gesture data |
| AWS Bedrock for multilingual feedback | Scales to any language without manual translation; handles nuanced corrective phrasing naturally |
| IndexedDB for local storage | Browser-native, no install, works offline, sufficient for progress data |
| PWA over native app | Cross-platform (desktop + mobile), installable, works offline, no app store required — ideal for schools and NGOs |
| Three-layer architecture | Separates concerns cleanly; edge layer works standalone; cloud layer enhances without being required |