# Noise Pollution Analytics: Citizen Complaint Intelligence System

A locally runnable academic prototype that converts synthetic citizen noise reports into structured, searchable signals and dashboard analytics. It is a civic decision-support tool; severity is AI-estimated and is not an official finding or enforcement decision.

## Features

- Complaint submission and NLP analysis: source, sentiment, estimated severity, urgency, keywords.
- TF-IDF and Logistic Regression source classifier, SQLite database, FastAPI endpoints.
- Admin dashboard with area/source/severity/sentiment charts, trend bars, search and filters, details, CSV export.
- 504 synthetic training rows and a seeder for 150 demo reports.
- Undergraduate report, model evaluation, notebooks, tests, and viva guide.

## Run on Windows

Python 3.10–3.13 is recommended. From the project root, start the backend in one terminal:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ml/train_models.py
python seed.py
uvicorn app.main:app --reload
```

In another terminal, serve the frontend:

```powershell
python -m http.server 5173 --directory frontend
```

Open http://127.0.0.1:5173. The API docs are at http://127.0.0.1:8000/docs. Python 3.14 dependencies may not all be available yet; use Python 3.12 if installation fails. Demo login credentials: `admin@demo.local` / `admin123`.

## NLP and model

The application lowercases and tokenizes text, removes a compact stopword list while preserving negation/intensifiers, applies a small transparent rule-based lemmatizer, computes unigram/bigram TF-IDF and classifies noise source using Logistic Regression. If model files are unavailable, a clearly identified keyword fallback keeps the local demo functional. Sentiment, severity and urgency are transparent lexical/rule baselines. Scores are not calibrated. Training uses a stratified 80/20 split with fixed seed and calculates accuracy, macro precision, recall, F1, per-class report and confusion matrix; metrics are written to `docs/model-results.md` by training.

## API summary

`POST /api/complaints/analyze`, `POST /api/complaints`, `GET /api/complaints` (filters: area, source, severity, sentiment_filter, search), `GET /api/complaints/{id}`, `GET /api/analytics/summary`, `by-source`, `by-area`, `by-severity`, `sentiment`, `trends`, and `GET /api/complaints/export`. Login/register demo endpoints are provided. See `/docs` for interactive API documentation.

Example request:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/complaints -H "Content-Type: application/json" -d '{"area":"Kharghar","complaint_text":"Every night extremely loud DJ music near our apartment until 1 AM. Elderly residents cannot sleep."}'
```

## Project structure

`frontend/` static responsive client; `backend/app/` API/NLP; `backend/ml/` training; `backend/tests/` tests; `data/noise_complaints.csv` synthetic dataset and generated SQLite DB; `models/` generated joblib artifacts; `notebooks/` guided notebooks; `docs/` report, API guide, results and viva answers. Dataset loading uses Python's built-in CSV support; no pandas dependency is needed.

## Screenshots

Add landing, analysis, and dashboard screenshots here.

## Limitations and future work

Synthetic template language and a compact English-only lexicon do not represent real reports. Rule-based sentiment and severity miss context; model scores are uncalibrated. Future work includes evaluating consented anonymized data, multilingual support, calibrated models, robust authentication, accessibility, and richer time analytics.
