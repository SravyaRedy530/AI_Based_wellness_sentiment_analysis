# 🧠 MoodMentor - AI Emotion Journal

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%20REST%20API-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Charts-Plotly-purple.svg)](https://plotly.com/)
[![Transformers](https://img.shields.io/badge/AI-DistilBERT%20%7C%20VADER%20%7C%20KeyBERT-yellow.svg)](https://huggingface.co/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite%20Fallback-orange.svg)](https://www.mysql.com/)

**MoodMentor** is a production-ready, full-stack AI-powered emotion journaling and psychological well-being platform. Designed with clean **Model-View-Controller (MVC)** architecture, MoodMentor transforms daily reflective writing into actionable mental wellness intelligence.

---

## 🌟 Key Features

1. **🔐 User Registration & Authentication**
   - Secure registration with email validation and `bcrypt` password hashing.
   - JWT (JSON Web Token) authentication with bearer authorization headers.
2. **🏠 Executive Wellness Dashboard**
   - Live metric cards (Total Entries, Daily Journaling Streak, Dominant Emotion, Average Sentiment).
   - Dynamic time-of-day greetings and daily motivational reflections.
   - Recent reflections preview cards with emotion badges and sentiment meters.
3. **⚡ Live Emotion Analysis Studio**
   - Real-time text analysis playground for immediate emotional diagnosis.
   - Multiclass emotion classification with confidence scores (Joy, Sadness, Anger, Fear, Love, Surprise).
   - VADER Sentiment Polarity scoring (Compound, Positive, Neutral, Negative).
   - Contextual keyphrase extraction using KeyBERT.
   - Personalized clinical and mindfulness coping strategies.
   - 1-click option to save analysis directly as a permanent journal entry.
4. **📖 Full-featured Journal Management**
   - Create, Read, Update, and Delete (CRUD) journal reflections with custom tags and dates.
   - Live search filter by keyword across titles, content, and tags.
   - Multi-parameter filtering by specific emotion or sentiment polarity.
   - Sorting by newest or oldest entries.
5. **📊 Deep Emotion Insights (Interactive Plotly Charts)**
   - **Donut Chart**: Comprehensive emotional distribution across your journaling history.
   - **Sentiment Timeline Line Chart**: Trajectory of sentiment scores with rolling 3-day trendline.
   - **Emotion Radar / Polar Chart**: Multidimensional emotional intensity profiling.
   - **Keywords Bar Chart**: High-frequency mood triggers and themes.
   - **Weekly Journaling Cadence**: Activity breakdown by day of the week.
   - **Psychological Trajectory Synthesis**: AI-driven behavioral commentary.
6. **👤 User Profile & Goal Management**
   - Manage display name, bio, and personalized wellness goals.
   - Secure password update functionality.
7. **📥 Export Journal CSV**
   - Full data portability: download complete journal history with emotion scores, sentiment metrics, and keywords in standard CSV format.
8. **⚠️ Account Deletion (Danger Zone)**
   - Secure permanent account deletion with password re-confirmation and cascading data erasure.

---

## 🏗️ Architecture & Technology Stack

MoodMentor follows a strict **Model-View-Controller (MVC)** pattern:

```
                            ┌────────────────────────────────────────┐
                            │               [V] VIEW                 │
                            │           Streamlit Client             │
                            │  (Responsive UI, Cards, Plotly Charts) │
                            └───────────────────┬────────────────────┘
                                                │  HTTP / JSON (JWT)
                                                ▼
                            ┌────────────────────────────────────────┐
                            │            [C] CONTROLLERS             │
                            │          Flask REST Blueprints         │
                            │   (Auth, Journal, Emotion, Analytics)  │
                            └─────────┬───────────────────┬──────────┘
                                      │                   │
                                      ▼                   ▼
                     ┌──────────────────────┐    ┌──────────────────────┐
                     │     AI SERVICES      │    │      [M] MODELS      │
                     │  • DistilBERT        │    │  SQLAlchemy ORM      │
                     │  • VADER Sentiment   │    │  • User              │
                     │  • KeyBERT Keywords  │    │  • JournalEntry      │
                     │  • Wellness Engine   │    │  • EmotionLog        │
                     └──────────────────────┘    └──────────┬───────────┘
                                                            │
                                                            ▼
                                                 ┌──────────────────────┐
                                                 │       DATABASE       │
                                                 │   MySQL 8.0+ /       │
                                                 │   SQLite Fallback    │
                                                 └──────────────────────┘
```

- **Frontend (`frontend/`)**: Streamlit, Custom Glassmorphic CSS, Plotly Express & Graph Objects.
- **Backend (`backend/`)**: Python, Flask, Flask-JWT-Extended, Flask-CORS, SQLAlchemy, PyMySQL.
- **AI Models (`backend/services/ai_service.py`)**:
  - **DistilBERT**: `bhadresh-savani/distilbert-base-uncased-emotion` for 6-class emotion prediction.
  - **VADER**: `nltk.sentiment.vader.SentimentIntensityAnalyzer` for lexical polarity.
  - **KeyBERT**: BERT embeddings for contextual n-gram keyword extraction.
- **Database (`database/`)**:
  - Primary: **MySQL** (`moodmentor_db`) with `database/schema.sql`.
  - Zero-config auto-fallback: **SQLite** (`instance/moodmentor.db`) ensures instant execution if MySQL credentials are not yet supplied.

---

## 📁 Project Folder Structure

`
MoodMentor/
├── frontend/                      # Streamlit User Interface
│   ├── app.py                     # Main Streamlit router & session controller
│   ├── pages/                     # Streamlit multi-page views
│   │   ├── 1_Overview.py          # Overview & emotional pulse
│   │   ├── 2_Analyze_Text.py      # Live AI emotion analysis
│   │   ├── 3_My_Journal.py        # Journal cards & CSV download
│   │   ├── 4_Insights.py          # Plotly visual telemetry
│   │   └── 5_My_Profile.py        # Profile & account settings
│   ├── components/                # Reusable UI widgets
│   │   ├── cards.py               # Metric cards, emotion badges, action plans
│   │   ├── charts.py              # Plotly Pie, Donut, Timeline & Radar charts
│   │   └── sidebar.py             # Sidebar navigation & weekly goal progress
│   ├── views/                     # MVC view modules
│   │   ├── dashboard_view.py      # Overview page renderer
│   │   ├── analyze_view.py        # Analyze Text page renderer
│   │   ├── journal_view.py        # My Journal page renderer
│   │   ├── insights_view.py       # Insights page renderer
│   │   ├── profile_view.py        # My Profile page renderer
│   │   └── export_view.py         # CSV Export page renderer
│   ├── assets/
│   │   └── styles.css             # Professional blue-purple SaaS stylesheet
│   ├── api_client.py              # HTTP client with JWT Bearer auth
│   └── config.py                  # Frontend color tokens & API base URL
│
├── backend/                       # Flask RESTful API Engine
│   ├── app.py                     # Flask application factory, CORS & JWT config
│   ├── routes/                    # Modular API route blueprints
│   │   ├── auth_routes.py         # Authentication (register, login, me, logout)
│   │   ├── journal_routes.py      # Journal CRUD & CSV export
│   │   ├── emotion_routes.py      # Real-time emotion & sentiment analysis
│   │   ├── analytics_routes.py    # Metric telemetry & Plotly datasets
│   │   ├── user_routes.py         # User profile & account management
│   │   └── rest_routes.py         # 10 root unified REST endpoints
│   ├── models/                    # SQLAlchemy database entities
│   │   ├── database.py            # Database engine & connection manager
│   │   ├── user.py                # User entity with bcrypt hashing
│   │   ├── journal.py             # JournalEntry entity
│   │   ├── emotion_log.py         # EmotionLog entity
│   │   └── suggestion.py          # Suggestion entity
│   ├── services/                  # Business logic services
│   │   ├── ai_service.py          # DistilBERT, VADER, KeyBERT, Coping engine
│   │   ├── journal_service.py     # Journal CRUD & CSV export routines
│   │   └── analytics_service.py   # Aggregations & Plotly chart data
│   ├── database/                  # Database connection & lifecycle
│   │   ├── __init__.py            # db session and initializer
│   │   └── connection.py          # Connection lifecycle verification
│   ├── utils/                     # Helpers & formatters
│   │   └── helpers.py             # Standard JSON response wrappers
│   ├── ai/                        # Dedicated AI pipelines
│   │   ├── emotion_model.py       # DistilBERT text classification
│   │   ├── sentiment_analyzer.py  # VADER sentiment polarity scorer
│   │   └── recommender.py         # Personalized wellness rule engine
│   └── config.py                  # Backend configuration & environment variables
│
├── database/                      # MySQL database scripts
│   ├── schema.sql                 # MySQL schema with tables, FKs, indexes
│   └── db_init.py                 # Automated MySQL table creation script
│
├── static/                        # Static assets, styling & icons
│   └── css/
│       └── styles.css             # Professional blue-purple SaaS styling
│
├── tests/                         # Automated test suites
│   ├── test_rest_apis.py          # Complete 10-endpoint REST verification
│   ├── test_csv_export.py         # 5-column CSV export verification
│   ├── test_auth.py               # Authentication & bcrypt tests
│   ├── test_analyzer.py           # DistilBERT & VADER analysis tests
│   ├── test_insights.py           # Plotly analytics & KPI tests
│   └── test_profile.py            # Profile & account lifecycle tests
│
├── requirements.txt               # Pinned Python package dependencies
├── README.md                      # Comprehensive project guide & API docs
├── run.py                         # Unified multi-process launcher
└── .env                           # Environment configuration
`

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- (Optional) MySQL Server 8.0+

### 2. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
1. Open the `.env` file.
2. If using **MySQL**:
   - Create the database in MySQL:
     ```sql
     CREATE DATABASE moodmentor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```
   - Update your MySQL credentials in `.env`:
     ```ini
     DB_HOST=localhost
     DB_PORT=3306
     DB_USER=root
     DB_PASSWORD=your_password_here
     DB_NAME=moodmentor_db
     USE_SQLITE_FALLBACK=True
     ```
   - Run the initialization script:
     ```bash
     python database/db_init.py
     ```
3. If MySQL credentials are not provided, MoodMentor **automatically activates the SQLite fallback** (`instance/moodmentor.db`), allowing you to test and run all features immediately with zero configuration!

---

## 🏃 Running the Application

### Option A: One-Click in Visual Studio Code (Recommended)
1. Open the project folder in VS Code (`File` > `Open Folder...`).
2. Press `F5` (or click **Run and Debug** in the left sidebar and select **"MoodMentor: Full Application (Unified)"**).
3. Both the Flask REST Backend (port 5000) and the Streamlit UI (port 8501) will launch automatically with full debugging support.
4. Your browser will open or navigate to `http://localhost:8501`.

*Alternative VS Code Launch Configurations:*
- **Backend: Flask REST API (Port 5000)** - debug Flask backend only.
- **Frontend: Streamlit UI (Port 8501)** - debug Streamlit frontend only.
- **Debug Both: Backend + Streamlit** - compound multi-target debugging.
- **Run Tasks** (`Ctrl+Shift+P` > `Tasks: Run Task` > `Run Full MoodMentor Stack`).

### Option B: Terminal Command Launcher
Launch both the Flask REST Backend and Streamlit Frontend with a single command:
```bash
python run.py
```
- **Streamlit Frontend**: `http://localhost:8501`
- **Flask REST API**: `http://localhost:5000/api/health`

### Option C: Run Services in Separate Terminals
**Terminal 1 (Backend API):**
```bash
python backend/app.py
```

**Terminal 2 (Streamlit UI):**
```bash
streamlit run frontend/app.py
```

---

## 🧪 Running Automated Tests

A comprehensive test suite is included to verify authentication, JWT security, AI pipelines, journal CRUD, analytics aggregation, and account deletion:
```bash
python tests/test_backend.py
```

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health` | Service health status and active database | No |
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT access token | No |
| `GET` | `/api/auth/me` | Fetch authenticated user details | Yes (JWT) |
| `POST` | `/api/emotion/analyze` | Real-time AI Emotion Analysis studio | Optional |
| `GET` | `/api/journal` | List & filter journal entries | Yes (JWT) |
| `POST` | `/api/journal` | Create journal entry with AI inference | Yes (JWT) |
| `GET` | `/api/journal/<id>` | Retrieve specific journal entry | Yes (JWT) |
| `PUT` | `/api/journal/<id>` | Update journal entry and refresh analysis | Yes (JWT) |
| `DELETE`| `/api/journal/<id>` | Delete journal entry | Yes (JWT) |
| `GET` | `/api/journal/export/csv` | Download complete journal history as CSV | Yes (JWT) |
| `GET` | `/api/analytics/dashboard` | Dashboard metrics, streak, and quote | Yes (JWT) |
| `GET` | `/api/analytics/insights` | Datasets for Plotly charts | Yes (JWT) |
| `GET` | `/api/user/profile` | View profile and wellness goals | Yes (JWT) |
| `PUT` | `/api/user/profile` | Update profile information | Yes (JWT) |
| `PUT` | `/api/user/password` | Change account password | Yes (JWT) |
| `DELETE`| `/api/user/delete-account` | Permanently delete account and cascade | Yes (JWT) |

---

## 🛡️ License & Credits
Developed with ❤️ using HuggingFace Transformers, NLTK, KeyBERT, Flask, and Streamlit.
MoodMentor is distributed under the MIT License.
