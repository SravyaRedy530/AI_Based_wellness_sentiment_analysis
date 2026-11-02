# Infosys Springboard Virtual Internship

# Project Name: AI-Based Employee Wellness Management Platform
## Product: MoodMentor – Intelligent Emotion Journal & Mental Wellness Analytics Platform

**Name:** Suzanne Kathyrene Thodeti  
**Date:** October 2026  
**Milestone:** Full-Stack AI Emotion Journal & Wellness Analytics Platform Documentation  

---

## Introduction

The **AI-Based Employee Wellness Management Platform (MoodMentor)** is an enterprise-grade, full-stack mental well-being and emotional intelligence system designed to combat workplace burnout, stress, and anxiety. In modern corporate environments, chronic psychological fatigue often develops unnoticed, diminishing employee satisfaction, engagement, and productivity. Traditional journaling tools act merely as passive digital diaries—they archive raw text without offering proactive diagnosis, emotional awareness, or psychological guidance.

**MoodMentor** bridges this gap by merging state-of-the-art **Natural Language Processing (NLP)**, **transformer-based deep learning**, and **evidence-based clinical coping interventions** into a cohesive daily reflection tool. As employees log their daily experiences, MoodMentor diagnoses nuanced emotional states, evaluates sentiment valence, extracts core workplace themes, and generates actionable, personalized coping strategies. Concurrently, an interactive visual telemetry engine enables users to track long-term emotional trajectories, encouraging early self-awareness and proactive psychological resilience.

### Key Highlights:
- **Decoupled MVC Architecture**: A modular Flask RESTful API backend communicating with a responsive, glassmorphic Streamlit client via strict JSON contracts and JWT Bearer authorization.
- **Hybrid AI Inference Pipeline**: Dual-engine intelligence utilizing fine-tuned transformer **DistilBERT** for 6-class emotion classification alongside **NLTK VADER** for fine-grained sentiment polarity.
- **Contextual Theme Extraction**: Utilizes **KeyBERT** embeddings to pinpoint recurring workplace triggers and thematic stressors.
- **Personalized Coping Recommender**: Deterministic clinical rule engine delivering immediate, scientifically backed interventions tailored to the detected emotion (e.g., 4-7-8 breathing for *Fear*, cognitive reframing for *Sadness*, gratitude celebration for *Joy*).
- **Comprehensive Journal Management**: Full CRUD capabilities with interactive cards displaying emotion badges, confidence scores, sentiment indicators, dynamic search filters (by emotion and keyword), and chronological sorting.
- **Plotly Visual Telemetry**: Deep analytical dashboard with interactive Donut distribution charts, a 3-day rolling trendline sentiment timeline, multi-axis emotion radar charts, and weekly cadence heatmaps.
- **Enterprise-Grade Relational Persistence**: Robust MySQL 8.0 schema featuring foreign keys, cascading deletions, and database indexes, paired with an automated zero-config SQLite fallback.
- **Data Sovereignty & Security**: Salted `bcrypt` password hashing, token blocklisting, 1-click 5-column CSV data export (`Date,Emotion,Sentiment,Journal,Confidence`), and GDPR-compliant cascading account erasure.

---

## Tech Stack

- **Frontend Framework**: **Streamlit (v1.38+)** — Delivers a reactive single-page/multi-page web application using pure Python, enhanced with custom glassmorphic CSS tokens, responsive metrics, and dynamic modals.
- **Backend API**: **Python 3.10+ / Flask (v3.0+)** — Enterprise RESTful API built on the application factory pattern with modular Flask Blueprints, CORS middleware, and structured HTTP response handlers.
- **Authentication & Security**: **Flask-JWT-Extended** & **bcrypt** — Stateless JSON Web Token authentication with Bearer tokens, token expiration, authorization headers, and cryptographically salted password hashes.
- **Deep Learning / Emotion NLP**: **Hugging Face Transformers (`DistilBERT`)** — Fine-tuned model (`bhadresh-savani/distilbert-base-uncased-emotion`) classifying reflections into 6 distinct classes: *Joy, Sadness, Anger, Fear, Love, Surprise*.
- **Lexical Sentiment Analysis**: **NLTK VADER (`SentimentIntensityAnalyzer`)** — Rule-based sentiment analyzer computing compound, positive, neutral, and negative polarity scores tailored for informal and expressive text.
- **Keyword & Theme Extraction**: **KeyBERT** — Contextual sentence-transformer embeddings extracting high-relevance workplace keywords and stressor n-grams.
- **Data Visualization**: **Plotly Express & Plotly Graph Objects** — High-performance interactive visual charts (Donut, Line, Radar, Bar) rendered natively in Streamlit.
- **Database Layer**: **MySQL 8.0+ / SQLAlchemy ORM** with **PyMySQL** driver — Relational data persistence with foreign keys, indexes, and constraints; backed by an automatic SQLite fallback (`instance/moodmentor.db`) for zero-configuration portability.
- **Data Portability**: **Pandas** — Powers analytical aggregations and dynamic CSV generation with exact standardized column schemas.
- **Unified Process Orchestrator**: Multi-process launcher (`run.py`) executing Flask and Streamlit simultaneously with sub-process health monitoring and graceful SIGINT termination.

---

## Project Structure

The project strictly adheres to the **Model-View-Controller (MVC)** architectural pattern, separating UI presentation, business logic, data models, and persistence:

```
MoodMentor/
├── frontend/                               # View Layer (Streamlit Client)
│   ├── app.py                              # Main application entry point & router
│   ├── api_client.py                       # HTTP client handling REST requests & JWT tokens
│   ├── config.py                           # Frontend theme tokens, styling & endpoint constants
│   ├── pages/                              # Multi-page views
│   │   ├── 1_Overview.py                   # Executive dashboard view
│   │   ├── 2_Analyze_Text.py               # Real-time AI emotion studio
│   │   ├── 3_My_Journal.py                 # Journal cards, search, filter & CSV export
│   │   ├── 4_Insights.py                   # Plotly analytical telemetry dashboard
│   │   └── 5_My_Profile.py                 # User profile, goals & danger zone
│   ├── components/                         # Modular UI reusable widgets
│   │   ├── cards.py                        # KPI metric cards, emotion badges & action cards
│   │   ├── charts.py                       # Plotly chart builders (Donut, Timeline, Radar)
│   │   └── sidebar.py                      # Navigation sidebar, user greeting & logout
│   ├── views/                              # Dedicated view-controller presentation modules
│   │   ├── dashboard_view.py               # Overview dashboard renderer
│   │   ├── analyze_view.py                 # Emotion analysis view renderer
│   │   ├── journal_view.py                 # Journal CRUD card renderer
│   │   ├── insights_view.py                # Visual telemetry renderer
│   │   ├── profile_view.py                 # User profile & account lifecycle renderer
│   │   ├── login_view.py                   # User authentication login modal
│   │   └── register_view.py                # New account registration modal
│   └── assets/
│       └── styles.css                      # Professional blue-purple glassmorphic stylesheet
│
├── backend/                                # Controller & Model Layer (Flask REST API)
│   ├── app.py                              # Flask application factory, CORS & JWT config
│   ├── config.py                           # Application configuration & database URI mapping
│   ├── controllers/                        # Controller logic handlers
│   │   ├── auth_controller.py              # Registration, login, token refresh
│   │   ├── journal_controller.py           # Journal CRUD & CSV streaming
│   │   ├── emotion_controller.py           # Real-time text inference controller
│   │   ├── analytics_controller.py         # Visual KPI aggregations & telemetry
│   │   ├── user_controller.py              # Profile updating & account deletion
│   │   └── rest_controller.py              # 10 root-level REST conventions
│   ├── routes/                             # Modular REST API Blueprints
│   │   ├── auth_routes.py                  # /api/auth routes
│   │   ├── journal_routes.py               # /api/journal routes
│   │   ├── emotion_routes.py               # /api/emotion routes
│   │   ├── analytics_routes.py             # /api/analytics routes
│   │   ├── user_routes.py                  # /api/user routes
│   │   └── rest_routes.py                  # Root REST blueprint mappings
│   ├── models/                             # Model Layer (SQLAlchemy ORM Entities)
│   │   ├── database.py                     # SQLAlchemy session & db instance
│   │   ├── user.py                         # User entity with bcrypt hashing
│   │   ├── journal.py                      # JournalEntry entity
│   │   ├── emotion_log.py                  # EmotionLog entity with AI telemetry
│   │   └── suggestion.py                   # Suggestion entity for coping strategies
│   ├── services/                           # Business Logic Services
│   │   ├── ai_service.py                   # DistilBERT, VADER, KeyBERT singleton engine
│   │   ├── journal_service.py              # Journal business logic & CSV generation
│   │   └── analytics_service.py            # Aggregations, distribution & trendlines
│   ├── ai/                                 # Specialized AI Pipelines
│   │   ├── emotion_model.py                # Transformer emotion inference wrapper
│   │   ├── sentiment_analyzer.py           # VADER polarity scoring wrapper
│   │   └── recommender.py                  # Rule-based psychological intervention engine
│   ├── database/
│   │   ├── __init__.py                     # Session initializers
│   │   └── connection.py                   # Connection lifecycle & fallback detection
│   └── utils/
│       └── helpers.py                      # Standardized JSON response formatters
│
├── database/                               # Database Schemas & Initializers
│   ├── schema.sql                          # MySQL 8.0 schema (DDL, FKs, Indexes)
│   └── db_init.py                          # Automated MySQL database initializer script
│
├── static/css/
│   └── styles.css                          # Shared CSS styling tokens
│
├── tests/                                  # Automated Test Verification Suite
│   ├── test_rest_apis.py                   # 10-endpoint REST specification test
│   ├── test_csv_export.py                  # 5-column CSV verification test
│   └── test_backend.py                     # Full auth, AI, CRUD & cascade test suite
│
├── .vscode/                                # VS Code Integration
│   ├── launch.json                         # 1-click F5 debugging configurations
│   ├── tasks.json                          # Automated execution tasks
│   └── settings.json                       # Workspace environment configurations
│
├── requirements.txt                        # Pinned production Python dependencies
├── README.md                               # Project quickstart & documentation
├── run.py                                  # Unified multi-process launcher script
└── .env                                    # Environment variable configuration
```

---

## Objectives

The core objectives successfully achieved in this milestone are:

### 1. Emotion & Sentiment Classification
- Implement real-time multiclass emotion diagnosis predicting 6 core emotional states (*Joy, Sadness, Anger, Fear, Love, Surprise*) using transformer deep learning.
- Provide continuous confidence scoring ($0.0\% - 100.0\%$) for emotional transparency.
- Compute granular lexical sentiment polarity (*Compound, Positive, Neutral, Negative*) via VADER NLP.
- Extract high-impact contextual workplace keywords using KeyBERT embeddings.

### 2. Personalized Wellness Suggestions Engine
- Develop a clinically aligned recommendation engine generating immediate, structured JSON suggestions based on the primary emotion:
  - **Joy**: Celebrate achievements, share appreciation, take photos, maintain gratitude log.
  - **Fear / Stress**: 4-7-8 breathing exercise, 5-4-3-2-1 grounding technique, positive affirmations, mindfulness anchor.
  - **Sadness**: Uplifting music therapy, therapeutic nature walk, reach out to a trusted friend, cathartic journaling.
  - **Anger**: Cooling sensory pause, physical movement discharge, objective perspective reframing.

### 3. Comprehensive Journal Management (CRUD)
- Enable employees to save reflections automatically with associated emotion telemetry and coping suggestions.
- Render stored entries in a responsive card layout featuring emotion badges, sentiment polarity tags, full reflection text, timestamps, and confidence meters.
- Support live keyword search across titles and reflection content.
- Support dynamic multi-category filtering by specific emotion and sentiment polarity.
- Implement chronological sorting (Newest First vs. Oldest First).
- Provide individual entry deletion with instant database synchronization.

### 4. Visual Telemetry & Analytics Dashboard (Plotly)
- Render an **Emotion Distribution Donut Chart** displaying proportional breakdown of emotional states.
- Render a **Sentiment Timeline** tracking emotional trajectory with a rolling 3-day trendline.
- Render a **Multidimensional Emotion Radar Chart** mapping emotional intensity across all 6 axes.
- Render a **Stressor Keywords Bar Chart** highlighting high-frequency triggers.
- Render an **Executive Overview** computing total check-ins, current journaling streak, positive vs. negative percentage balance, and most frequent emotional state.

### 5. Profile Management & Secure Data Portability
- Maintain user profiles with customizable full name, email, preferred support style (*Mindful, Action-Oriented, Analytical*), and UI theme settings.
- Implement standardized **CSV Journal Export** generating downloadable files with the exact required schema:
  `Date,Emotion,Sentiment,Journal,Confidence`.
- Provide a secure **Danger Zone** for permanent account deletion with password verification and cascading database eradication.

### 6. Relational Database Architecture & Persistence
- Design and implement a robust MySQL 8.0 schema featuring foreign keys, constraints, and performance indexes.
- Provide zero-config SQLite automatic fallback to guarantee uninterrupted execution in any development environment.

---

## Code Implementation

The project implementation leverages Python 3.10+ as the core language, Flask as the backend REST engine, and Streamlit as the interactive frontend framework. Below are the key modules:

### Module 1: AI Emotion & Sentiment Analysis (`backend/services/ai_service.py`)
This module encapsulates the deep learning and NLP models. It runs as a thread-safe singleton, preloading DistilBERT, VADER, and KeyBERT during backend initialization to eliminate cold-start latency.

```python
class AIService:
    """Core AI Engine integrating DistilBERT, VADER, and KeyBERT."""

    def analyze_emotion_distilbert(self, text: str) -> Dict[str, Any]:
        """Classifies text into 6 emotions with confidence scores."""
        truncated_text = text[:512]
        predictions = self.emotion_classifier(truncated_text)[0]
        sorted_preds = sorted(predictions, key=lambda x: x["score"], reverse=True)
        primary = sorted_preds[0]
        
        all_scores = {p["label"].capitalize(): round(float(p["score"]), 4) for p in sorted_preds}
        return {
            "dominant_emotion": primary["label"].capitalize(),
            "confidence": round(float(primary["score"]), 4),
            "all_scores": all_scores
        }

    def analyze_sentiment_vader(self, text: str) -> Dict[str, Any]:
        """Calculates lexical polarity compound and component scores."""
        scores = self.sentiment_analyzer.polarity_scores(text)
        compound = scores["compound"]
        label = "Positive" if compound >= 0.05 else ("Negative" if compound <= -0.05 else "Neutral")
        return {
            "compound": round(compound, 4),
            "sentiment": label,
            "positive": round(scores["pos"], 4),
            "neutral": round(scores["neu"], 4),
            "negative": round(scores["neg"], 4)
        }
```

---

### Module 2: Personalized Coping & Suggestion Engine (`backend/ai/recommender.py`)
This module maps diagnosed emotional states into targeted, scientifically grounded psychological suggestions and returns structured JSON arrays:

```python
def get_personalized_suggestions(emotion: str) -> Dict[str, Any]:
    """Generates tailored coping strategies formatted as JSON."""
    normalized = emotion.capitalize()
    
    suggestion_matrix = {
        "Joy": [
            {"category": "Celebration", "text": "Celebrate achievements and savor today's success."},
            {"category": "Appreciation", "text": "Share appreciation with someone who helped you."},
            {"category": "Memory", "text": "Take photos or save a keepsake of this positive moment."}
        ],
        "Fear": [
            {"category": "Breathing", "text": "Practice 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s."},
            {"category": "Grounding", "text": "Use the 5-4-3-2-1 sensory grounding technique."},
            {"category": "Affirmation", "text": "Repeat positive affirmations: 'I am safe and capable.'"},
            {"category": "Mindfulness", "text": "Anchor yourself in the present moment through mindfulness."}
        ],
        "Sadness": [
            {"category": "Music Therapy", "text": "Listen to comforting or uplifting music."},
            {"category": "Nature Walk", "text": "Take a 15-minute gentle walk outdoors in natural light."},
            {"category": "Social Connection", "text": "Reach out to a trusted friend or colleague for a chat."},
            {"category": "Journaling", "text": "Engage in cathartic, non-judgmental expressive writing."}
        ]
    }
    return {
        "emotion": normalized,
        "suggestions": suggestion_matrix.get(normalized, [
            {"category": "Mindfulness", "text": "Take a brief pause, drink water, and reflect gently."}
        ])
    }
```

---

### Module 3: REST API Controllers & Security Layer (`backend/controllers/rest_controller.py`)
This module exposes 10 standardized REST endpoints, managing JWT Bearer tokens and returning consistent JSON responses:

```python
@rest_bp.route("/analyze", methods=["POST"])
def analyze():
    """POST /analyze: Run AI emotion, sentiment, and suggestion pipelines."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"success": False, "error": "Journal text is required"}), 400

    analysis = ai_service.analyze_full_entry(text)
    return jsonify({
        "success": True,
        "emotion": analysis["dominant_emotion"],
        "confidence": analysis["confidence"],
        "sentiment": analysis["sentiment"],
        "sentiment_score": analysis["sentiment_score"],
        "keywords": analysis["keywords"],
        "suggestions": analysis["suggestions"]
    }), 200

@rest_bp.route("/journal", methods=["GET"])
@jwt_required()
def get_journal_entries():
    """GET /journal: Retrieve user reflections with search, filter, and sorting."""
    user_id = int(get_jwt_identity())
    emotion_filter = request.args.get("emotion")
    search_keyword = request.args.get("search")
    sort_order = request.args.get("sort", "latest")

    entries = journal_service.get_user_entries(
        user_id=user_id,
        emotion=emotion_filter,
        search=search_keyword,
        sort=sort_order
    )
    return jsonify({"success": True, "count": len(entries), "data": entries}), 200
```

---

### Module 4: Relational Database Layer (`database/schema.sql` & `backend/models/`)
The persistence layer defines the relational schema with foreign key constraints, indexes, and cascading deletions across 4 primary entities:

```sql
-- MySQL 8.0 Relational Schema
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    support_style VARCHAR(50) DEFAULT 'Mindful',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS journal_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) DEFAULT 'Daily Reflection',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_journal_user (user_id),
    INDEX idx_journal_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS emotion_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    journal_id INT NOT NULL UNIQUE,
    dominant_emotion VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    sentiment_score FLOAT NOT NULL,
    sentiment_label VARCHAR(50) NOT NULL,
    all_scores JSON,
    keywords VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (journal_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
    INDEX idx_dominant_emotion (dominant_emotion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    journal_id INT NOT NULL,
    category VARCHAR(100) NOT NULL,
    recommendation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (journal_id) REFERENCES journal_entries(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

### Module 5: Streamlit Frontend & Glassmorphism UI (`frontend/app.py`)
The main Streamlit client manages session states, JWT storage, page navigation, and renders modern glassmorphism cards and Plotly figures:

```python
import streamlit as st
from frontend.api_client import api_client
from frontend.components.sidebar import render_sidebar
from frontend.views.dashboard_view import render_dashboard
from frontend.views.analyze_view import render_analyze
from frontend.views.journal_view import render_journal
from frontend.views.insights_view import render_insights
from frontend.views.profile_view import render_profile

st.set_page_config(
    page_title="MoodMentor | AI Emotion Journal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render professional sidebar navigation
current_page = render_sidebar()

# Route to respective MVC View
if current_page == "Overview":
    render_dashboard()
elif current_page == "Analyze Text":
    render_analyze()
elif current_page == "My Journal":
    render_journal()
elif current_page == "Insights":
    render_insights()
elif current_page == "My Profile":
    render_profile()
```

---

### Module 6: Multi-Process Orchestrator (`run.py`)
A single-command launcher that initializes both the Flask backend and Streamlit frontend in separate subprocesses with clean health monitoring:

```python
def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    python_exe = sys.executable

    # 1. Start Flask REST API (Port 5000)
    backend_script = os.path.join(base_dir, "backend", "app.py")
    backend_proc = subprocess.Popen([python_exe, backend_script], cwd=base_dir)

    time.sleep(2)  # Allow backend to initialize database connections

    # 2. Start Streamlit Frontend (Port 8501)
    frontend_script = os.path.join(base_dir, "frontend", "app.py")
    frontend_proc = subprocess.Popen([
        python_exe, "-m", "streamlit", "run", frontend_script,
        "--server.port=8501", "--server.headless=true"
    ], cwd=base_dir)

    print("[OK] MoodMentor LIVE at http://localhost:8501 (API: http://localhost:5000)")
```

---

## System Flow

The end-to-end data lifecycle flows through the platform as follows:

```
[Employee Enters Reflection]
           │
           ▼
[Streamlit Frontend UI]
           │  HTTP POST /api/analyze (JSON + JWT)
           ▼
[Flask REST Blueprint Controller]
           │
           ├──► [DistilBERT Transformer] ──► 6-Class Emotion + Confidence (%)
           ├──► [VADER Sentiment Engine] ──► Compound Polarity Score (-1 to +1)
           ├──► [KeyBERT Embedding]      ──► Contextual Keyword Tags
           └──► [Clinical Rule Engine]   ──► Personalized Coping Suggestions (JSON)
           │
           ▼
[SQLAlchemy ORM Data Persistence]
           │
           ├──► Primary: MySQL 8.0 (Users, JournalEntries, EmotionResults, Suggestions)
           └──► Fallback: SQLite (`instance/moodmentor.db`)
           │
           ▼
[Interactive UI Presentation]
           │
           ├──► "My Journal": Interactive Cards (Emotion Badge, Polarity, Keywords, Delete)
           ├──► "Insights": Plotly Donut, Sentiment Timeline, Radar Chart, Cadence
           └──► "Profile": 5-Column CSV Export (`Date,Emotion,Sentiment,Journal,Confidence`)
```

1. **User Authentication**: The employee registers or logs in; the backend validates credentials using `bcrypt` and issues a signed JWT access token stored in Streamlit session state.
2. **Text Submission**: The employee types their reflection in the **Analyze Text** studio or **My Journal** interface.
3. **AI Pipeline Execution**: The Flask backend processes the raw text through DistilBERT for emotion classification, VADER for sentiment scoring, and KeyBERT for theme extraction.
4. **Clinical Suggestion Synthesis**: The recommender evaluates the primary emotion and attaches targeted psychological coping strategies.
5. **Relational Persistence**: All data is saved transactionally across `journal_entries`, `emotion_results`, and `suggestions` tables.
6. **Card Rendering**: The **My Journal** page renders responsive reflection cards equipped with real-time keyword search, emotion filtering, and sorting.
7. **Telemetry Aggregation**: The **Insights** page queries historical records and generates interactive Plotly visualizations.
8. **Data Export**: The user can export their complete historical record as an audit-ready CSV file at any time.

---

## How to Run

### Prerequisites:
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- VS Code or modern terminal.
- (Optional) MySQL Server 8.0+ running on port 3306.

### Setup Steps:

```powershell
# Step 1: Navigate to project workspace
cd C:\Users\sravy\OneDrive\Desktop\AI_Based_Employee_Wellness_Managment_Platfor

# Step 2: Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows PowerShell

# Step 3: Install all required dependencies
pip install -r requirements.txt

# Step 4: Configure Environment & Database
# (Optional) Update .env with MySQL credentials if using MySQL server
# Run the automated database initialization script
python database/db_init.py

# Step 5: Launch the complete Full-Stack Application
python run.py
```

### Access Endpoints:
- **Streamlit Web Application**: [http://localhost:8501](http://localhost:8501)
- **Flask REST API Health Check**: [http://localhost:5000/api/health](http://localhost:5000/api/health)

---

## Output Screenshots & UI Walkthrough

### 1. Executive Overview Dashboard
The Overview page presents a high-level emotional summary upon login. It features live metric cards showing Total Journal Entries, Daily Journaling Streak, Dominant Emotional State, and Average Sentiment Polarity. A dynamic time-of-day greeting, motivational reflection quote, and recent entry cards provide immediate context.

*Fig 1: Executive Overview Dashboard with live KPI counters, journaling streak, and recent reflection preview cards.*

---

### 2. Live AI Emotion Analysis Studio
The Analyze Text page provides a real-time diagnosis studio. When an employee inputs text describing workplace stress, the AI pipeline executes sub-second inference. It renders the primary emotion with an animated confidence bar, the VADER sentiment polarity meter, extracted KeyBERT keywords, and personalized clinical coping cards. An integrated **Save Analysis to Journal** button commits the record directly to MySQL.

*Fig 2: Real-Time AI Emotion Analysis Studio displaying DistilBERT classification, VADER sentiment, KeyBERT themes, and personalized coping strategies.*

---

### 3. My Journal — Interactive Cards, Search & Filtering
The My Journal page renders all saved entries as glassmorphic cards. Each card displays a color-coded emotion badge, sentiment label, formatted timestamp, full journal text, and individual delete button. Users can search entries by keyword in real time, filter by emotion (Joy, Fear, Sadness, etc.), and toggle sorting between newest and oldest entries.

*Fig 3: My Journal management interface displaying responsive emotion cards with live search, emotion filtering, and sorting.*

---

### 4. Deep Emotion Insights (Plotly Telemetry)
The Insights dashboard translates subjective journal entries into objective psychological telemetry through four interactive Plotly charts:
- **Emotion Distribution (Donut Chart)**: Visualizes the proportion of time spent in each emotional state.
- **Sentiment Timeline (Line Chart)**: Tracks emotional valence over time with a 3-day rolling moving-average trendline.
- **Multidimensional Emotion Radar**: Displays the 6-axis emotional footprint.
- **Stressor Keywords (Horizontal Bar Chart)**: Analyzes high-frequency workplace triggers.

*Fig 4: Visual telemetry dashboard featuring interactive Plotly Donut, Sentiment Timeline, and Radar charts.*

---

### 5. Profile Management & CSV Export
The Profile page enables employees to update personal information and configure their preferred psychological support style (*Mindful, Action-Oriented, Analytical*). The **Export Journal to CSV** feature generates an immediate download with the verified 5-column format (`Date,Emotion,Sentiment,Journal,Confidence`). The **Danger Zone** permits secure, permanent account deletion with password re-authentication and cascading database eradication.

*Fig 5: Profile view featuring personalized support styles, 1-click CSV export, and GDPR-compliant cascading account deletion.*

---

## Known Limitations

- **Nuance & Sarcasm Detection**: While DistilBERT excels at emotional tone classification, subtle literary irony or enterprise sarcasm in very brief snippets (under 5 words) may occasionally be categorized based on literal lexical polarity.
- **Text-Only Modality**: The system currently accepts written text reflections. Multi-modal inputs such as acoustic voice recordings or video-based facial affect recognition are not yet integrated.
- **CPU Inference Scalability**: Under large concurrent enterprise spikes (e.g., thousands of simultaneous corporate submissions), transformer inference on CPU servers may experience slight queuing latency without dedicated GPU acceleration or model quantization (ONNX/TensorRT).

---

## Future Scope

- **Milestone 2: Multi-Modal Voice Analysis**: Integrate speech-to-text with acoustic prosody extraction (pitch, jitter, vocal energy) for audio-based voice journaling.
- **Milestone 3: Wearable Health Sensor Integration**: Connect smartwatches (Fitbit, Apple Health) to correlate physiological markers (Heart Rate Variability, sleep debt) with subjective emotional journal entries.
- **Milestone 4: Anonymized Corporate HR Insights**: Aggregate department-level emotional heatmaps and burnout risk indices with $k$-anonymity to protect individual privacy while helping leaders prevent organizational burnout.
- **Milestone 5: Conversational AI Wellness Copilot**: Provide a proactive, conversational agent utilizing Retrieval-Augmented Generation (RAG) to conduct interactive Cognitive Behavioral Therapy (CBT) reflection sessions.

---

## Conclusion

In this milestone, the **AI-Based Employee Wellness Management Platform (MoodMentor)** successfully establishes a robust, modern, and clinically grounded foundation for workplace mental wellness management. By decoupling the presentation layer from the Flask RESTful API and integrating state-of-the-art transformer NLP with evidence-based coping interventions, MoodMentor transforms routine daily journaling into actionable emotional intelligence.

The platform provides end-to-end data integrity through ACID-compliant MySQL storage, automated SQLite fallback, secure JWT authentication, and interactive Plotly telemetry. All milestone requirements—from multiclass emotion diagnosis and personalized suggestion generation to interactive card management and standard 5-column CSV export—have been verified with automated test suites. This milestone validates the full architectural stack, ensuring that MoodMentor is production-ready, performant, and extensible for future multi-modal and enterprise enhancements.
