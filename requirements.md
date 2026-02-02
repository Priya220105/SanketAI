# SanketAI — Requirements Document
## AI-Powered Sign Language Learning Platform
### AI for Bharat Hackathon | Track: AI for Learning & Developer Productivity

---

## 1. Problem Statement

India has **2.7 crore (27 million) deaf and hard-of-hearing learners**, but access to trained sign language educators is extremely limited — particularly in rural and Tier-2/3 regions. Fewer than 300 qualified Indian Sign Language (ISL) interpreters serve the entire country.

Three core failures exist in the current landscape:

- **Static solutions** — Existing learning tools are teacher-dependent and do not provide real-time corrective feedback.
- **Expensive and inaccessible** — Most platforms require expensive hardware, consistent internet, or one-on-one instructor time.
- **Internet-heavy** — Solutions requiring high bandwidth are unusable across 60% of rural India where reliable 4G is unavailable.

NGOs, schools, and families all lack scalable, affordable, and measurable ways to teach sign language consistently. Inclusive communication is not a privilege — it is a necessity for participation in education, employment, and society.

---

## 2. Objective

To build an AI-powered, interactive sign language learning platform that enables deaf and hard-of-hearing learners to practice Indian Sign Language (ISL) independently using real-time webcam-based gesture recognition, intelligent corrective feedback, and adaptive learning — all working offline-first on low-cost devices without special hardware.

---

## 3. Target Users

| User Segment | Primary Need | How SanketAI Serves Them |
|---|---|---|
| Deaf & hard-of-hearing students | Personalized, self-paced learning | Adaptive difficulty, corrective feedback, progress tracking |
| Children & parents | Learn together at home | Family Mode — parent + child practice side by side |
| Teachers & special educators | Reduced manual effort, visibility | Teacher dashboard, multi-student view, PDF reports |
| NGOs & inclusion programs | Scalable, measurable, reportable | Standardized training, accuracy analytics, WhatsApp sharing |
| Rural communities | Learning without connectivity | Offline-first edge AI, works on ₹5,000 tablets |

---

## 4. Functional Requirements

### 4.1 Sign Recognition & Learning Core
| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Webcam-based real-time hand gesture capture | Critical |
| FR-02 | On-device hand detection and landmark extraction using **MediaPipe** (21 landmarks per hand) | Critical |
| FR-03 | On-device sign recognition using a model prototyped with **Google Teachable Machine**, fine-tuned on ISL dataset | Critical |
| FR-04 | Real-time accuracy calculation by comparing learner's gesture against target sign | Critical |
| FR-05 | Explainable corrective feedback highlighting specific errors — hand shape, orientation, and movement timing | Critical |
| FR-06 | Multilingual feedback generation in English, Hindi, and extensible to regional languages via **AWS Bedrock** | Critical |

### 4.2 Learning Experience
| ID | Requirement | Priority |
|---|---|---|
| FR-07 | Split-screen learning mode — reference sign on one side, live webcam feed on the other | High |
| FR-08 | Three adaptive difficulty levels: Beginner → Intermediate → Advanced | High |
| FR-09 | Automatic level progression based on learner accuracy and performance | High |
| FR-10 | Scenario-based lesson modules: School, Home, Emotions | High |
| FR-11 | 50+ ISL signs across all levels | High |
| FR-12 | Multiple practice modes: Guided lessons, Free practice, Timed tests | High |

### 4.3 Family & Social Features
| ID | Requirement | Priority |
|---|---|---|
| FR-13 | Family Mode — parent and child learn signs together in a shared session | Medium |
| FR-14 | Essential survival signs prioritized first (e.g., "I love you", "Hungry?", "Help") | Medium |
| FR-15 | Shareable guest lessons — short 5-minute sign lessons via link | Medium |

### 4.4 Progress & Analytics
| ID | Requirement | Priority |
|---|---|---|
| FR-16 | Per-sign accuracy tracking over time with visual graphs | High |
| FR-17 | Weekly progress reports exportable as downloadable PDF | Medium |
| FR-18 | Teacher dashboard with multi-student progress view | Medium |
| FR-19 | Easy progress sharing via WhatsApp | Medium |
| FR-20 | Level completion tracking and learning history log | High |

### 4.5 Offline & Cloud Sync
| ID | Requirement | Priority |
|---|---|---|
| FR-21 | Full core functionality (sign recognition, feedback, practice) works offline | Critical |
| FR-22 | Local progress storage on user device | Critical |
| FR-23 | Optional asynchronous sync of anonymized progress data to **Amazon S3** when internet is available | Medium |

---

## 5. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-01 | Sign recognition inference latency | **< 500ms** on-device |
| NFR-02 | Model accuracy on ISL test set | **90%+** |
| NFR-03 | App initial load time | < 3 seconds |
| NFR-04 | Minimum device support | Basic laptop or tablet with webcam (e.g., ₹5,000 government-issued tablets) |
| NFR-05 | Bandwidth requirement | Works on 2G/3G; core features fully offline |
| NFR-06 | Data privacy | No video or facial image storage; no personally identifiable information retained; anonymized analytics only |
| NFR-07 | Scalability | Zero marginal cost per additional user; supports concurrent use across schools and NGOs |
| NFR-08 | Accessibility | Usable by children and non-technical users with no prior training |
| NFR-09 | Platform support | Web-based (Chrome, Firefox, Edge); future Android mobile app |

---

## 6. Technical Stack

| Layer | Component | Technology |
|---|---|---|
| **Frontend** | Web UI | HTML, CSS, JavaScript (React.js) |
| **Hand Tracking** | Landmark Detection | MediaPipe Holistic (21 landmarks per hand, runs on-device) |
| **ML Model** | Sign Recognition | Google Teachable Machine (prototyped) → fine-tuned on ISL dataset |
| **Edge Inference** | On-device Prediction | TensorFlow.js (browser-based, <500ms latency) |
| **Feedback Engine** | Corrective Guidance | Custom logic — compares predicted vs target sign, identifies error type |
| **Multilingual Feedback** | Language Generation | AWS Bedrock (Hindi, English, extensible to regional languages) |
| **Local Storage** | Offline Progress | IndexedDB (browser-native) |
| **Cloud Sync** | Progress & Analytics | Amazon S3 (anonymized, optional, asynchronous) |

---

## 7. User Stories

### Deaf & Hard-of-Hearing Student
> **As a** deaf student, **I want to** practice signs at my own pace with real-time feedback, **so that** I can learn independently without waiting for a teacher or tutor.

> **As a** deaf student, **I want the** app to tell me exactly what I did wrong (hand shape, angle, speed), **so that** I can correct my technique and improve quickly.

> **As a** deaf student, **I want** the difficulty to increase automatically as I improve, **so that** I stay challenged and keep making progress.

### Parent
> **As a** hearing parent of a deaf child, **I want to** learn signs alongside my child in Family Mode, **so that** we can communicate better at home.

> **As a** parent, **I want to** share short 5-minute sign lessons with my family, **so that** grandparents and relatives can also learn to communicate with my child.

> **As a** parent, **I want to** see my child's weekly progress report, **so that** I know if they are improving and where they need support.

### Teacher / Special Educator
> **As a** special educator, **I want a** dashboard that shows me the progress of all 15 students at once, **so that** I can identify who needs extra support without checking each student individually.

> **As a** teacher, **I want to** download a PDF report of each student's progress, **so that** I can share it with parents and include it in school records.

### NGO Coordinator
> **As an** NGO coordinator, **I want to** deploy SanketAI across 50 students with zero setup cost, **so that** I can scale our sign language program without hiring more instructors.

> **As an** NGO coordinator, **I want** standardized progress metrics and exportable reports, **so that** I can demonstrate measurable outcomes to donors and funding bodies.

---

## 8. Constraints

| Constraint | Details |
|---|---|
| No special hardware | Must work with a standard webcam on any basic laptop or tablet |
| Rural connectivity | 60% of target users have no reliable 4G — offline-first is non-negotiable |
| Cost | Zero cost per end user; platform must be free for learners |
| Ease of use | Usable by children (ages 8+) and non-technical adults with no training |
| AWS integration | Must meaningfully use AWS services (Bedrock for multilingual feedback, S3 for data sync) |
| Data ethics | No biometric data storage; consent-based processing; transparent AI feedback |

---

## 9. Success Metrics

| Metric | Target | Timeframe |
|---|---|---|
| Active learners | 10,000+ users | Year 1 |
| NGO / School partnerships | 50+ institutions | Year 1 |
| Sign accuracy improvement | 60% → 85%+ per learner | Within 4 weeks of use |
| Rural user penetration | 40% of users from Tier-2/3 cities | Year 1 |
| Signs practiced (platform-wide) | 500,000+ practice sessions | 6 months |
| Cost per user | ₹0 (free) | Launch |
| Teacher time saved | 1 teacher manages 50 students (vs 5 without AI) | At deployment |

---

## 10. Out of Scope (MVP)

The following features are planned for future phases and are **not** in the MVP:

- Regional sign language variations (beyond standard ISL)
- Full educator and NGO dashboards with engagement analytics
- Android mobile application
- Integration with government education platforms (e.g., DIKSHA)
- Emotion recognition via facial expression analysis
- Peer learning / social network features ("SanketSaathi")

---

## 11. Post-Hackathon Roadmap

| Phase | Timeline | Deliverables |
|---|---|---|
| **Phase 1 — MVP** | Months 1–3 | 50 ISL signs, web app, split-screen practice, basic corrective feedback, offline mode |
| **Phase 2 — Pilot & Scale** | Months 3–6 | NGO partnerships (10+), multilingual feedback (Hindi + English), mobile app (Android), 200+ signs |
| **Phase 3 — Full Platform** | Months 6–12 | Educator dashboards, regional language support, cloud analytics, 1,000+ signs, 50+ institutional partners |