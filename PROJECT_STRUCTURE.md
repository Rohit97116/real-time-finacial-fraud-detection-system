# FraudLens AI - Project Structure Guide

## 🏗️ Production Directory Layout

```
PROJECT-real time financial fraud detection system/
├── app.py                          # Main Flask WSGI application (entry point)
├── requirements.txt                # Python dependencies (pip install compatible)
├── render.yaml                     # Render.com deployment configuration
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── DEPLOY_GITHUB_RENDER.md         # Deployment instructions
├── PROJECT_STRUCTURE.md            # This file
│
├── services/                       # Business logic & ML services
│   ├── fraud_service.py            # Hybrid ML + rule-based fraud detection orchestrator
│   ├── feature_service.py          # ML feature engineering (8D vectors)
│   ├── model_service.py            # Isolation Forest ML model training & scoring
│   ├── pdf_parser_service.py       # PDF parsing orchestrator
│   ├── history_service.py          # Analysis history persistence (JSON)
│   └── __init__.py
│
├── reports/                        # Report generation
│   ├── export_service.py           # CSV & PDF report export
│   └── __init__.py
│
├── Templates/                      # Jinja2 HTML templates (9 pages)
│   ├── welcome.html                # Homepage with hero section
│   ├── analysis_mode.html          # Mode selection (single/multi/history)
│   ├── details_single.html         # Single-month analysis form
│   ├── details_multi.html          # Multi-file upload form
│   ├── combined_history.html       # Previous analysis retrieval
│   ├── result.html                 # Analysis results dashboard
│   ├── history.html                # Historical analyses table
│   ├── report.html                 # Interactive report with Chart.js
│   └── details.html                # (unused, replaced by analysis_mode.html)
│
├── statics/                        # Static assets
│   ├── css/
│   │   └── theme.css               # Dark mode responsive design (~1000+ lines)
│   └── img/
│       ├── fraud-hero.svg          # Hero section illustration
│       └── security-dashboard.svg  # Dashboard illustration
│
├── data/                           # Runtime data storage
│   └── analysis_history.json       # JSON array of past analyses (user-generated)
│
├── models/                         # ML model artifacts
│   ├── fraud_model.pkl             # Trained Isolation Forest model (generated)
│   └── __init__.py
│
├── pdf_reader.py                   # PDF text extraction utility (OCR fallback)
├── table_parser.py                 # Bank statement table parsing
└── transaction_parser.py           # Transaction data normalization

.git/                               # Git version control (not shown in workspace)
```

## 📋 File Purposes

### Core Application

| File | Purpose | Dependencies |
|------|---------|--------------|
| `app.py` | Flask WSGI app, routes, request handling | Flask, services/, reports/ |
| `render.yaml` | Render.com cloud deployment config | Gunicorn, Python 3.14 |
| `requirements.txt` | Project dependencies (flexible versions) | pip |

### Services Layer

| File | Purpose | Key Functions |
|------|---------|---------------|
| `fraud_service.py` | ML + rule-based fraud detection (85/15) | `analyze_with_ml(txn_df, profile)` |
| `feature_service.py` | Transaction feature engineering | `build_feature_frame(transactions)` |
| `model_service.py` | Isolation Forest ML model | `score_anomalies(features)` |
| `pdf_parser_service.py` | PDF parsing orchestrator | `parse_bank_statement(file_path)` |
| `history_service.py` | Analysis history persistence | `load_history_entries()`, `append_history_entry()` |

### Utilities

| File | Purpose | Key Functions |
|------|---------|---------------|
| `pdf_reader.py` | PDF text extraction with OCR fallback | `extract_text_from_pdf(path)` |
| `table_parser.py` | Bank statement table extraction | `extract_transactions_from_pdf(path)` |
| `transaction_parser.py` | Transaction normalization | `parse_transactions(data)` |

### Data & Models

| Folder | Purpose | Lifecycle |
|--------|---------|-----------|
| `data/` | Historical analysis persistence | Created at runtime, persisted |
| `models/` | ML model artifacts | Generated at app startup, reused |
| *removed* | `uploads/` (temp), `venv/` (env), `__pycache__/` | Ephemeral, not committed |

## 🔄 Data Flow

```
User Request (Browser)
    ↓
app.py routes
    ↓
services/fraud_service.py (orchestration)
    ├─→ services/pdf_parser_service.py (PDF parsing)
    │   ├─→ pdf_reader.py (text extraction)
    │   ├─→ table_parser.py (table parsing)
    │   └─→ transaction_parser.py (normalization)
    ├─→ services/feature_service.py (feature engineering)
    ├─→ services/model_service.py (ML scoring)
    └─→ Result object with risk_score, fraud_flag, fraud_level
    ↓
reports/export_service.py (CSV/PDF generation)
    ↓
services/history_service.py (persistence)
    ↓
Render HTTP Response (HTML/PDF/CSV)
```

## 🚀 Deployment

### Local Development
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
# http://127.0.0.1:5000
```

### Render Production
```bash
# render.yaml triggers:
1. pip install -r requirements.txt
2. gunicorn app:app --bind 0.0.0.0:$PORT
3. Auto health check at /
```

## 📊 Key Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Flask | 3.1.2 |
| ML Model | Isolation Forest (scikit-learn) | 1.x |
| Data Processing | Pandas + NumPy | 3.0.0, 2.4.1 |
| PDF Parsing | pdfplumber + pytesseract | 0.11.9, 0.3.13 |
| Report Generation | ReportLab | 4.4.9 |
| Web Server | Gunicorn | 21.2.0+ |
| Frontend | Jinja2 + Chart.js + CSS3 | 3.1+, CDN, responsive |
| Runtime | Python | 3.14 |

## 🎯 Production Checklist

- ✅ All old backups removed (app_old.py, fraud_detector_old.py)
- ✅ Docker config removed (.dockerignore - using Python runtime)
- ✅ Temporary files excluded (uploads/, __pycache__/, venv/)
- ✅ All imports working correctly
- ✅ WSGI alias configured (`application = app`)
- ✅ PORT environment variable support
- ✅ Requirements.txt Python 3.14 compatible
- ✅ Git tracking optimized (.gitignore negation patterns)
- ✅ Render auto-deploy configured (render.yaml)
- ✅ All 12 Flask routes operational
- ✅ All 9 HTML templates rendering correctly
- ✅ Static assets (CSS/SVG) loading correctly
- ✅ Report generation (CSV/PDF) functional
- ✅ History persistence working
- ✅ ML model training on startup

## 📁 Ignore Patterns (.gitignore)

```
# Environment & Build
venv/
__pycache__/
*.pyc
.env

# Runtime Generated
*.pkl
uploads/
*.pdf (except repo docs)

# Generated Reports
reports/*.csv
reports/*.pdf
data/analysis_history.json (in .gitignore)

# IDE & OS
.vscode/
.idea/
*.swp
.DS_Store
```

## 🔒 Security Notes

1. **PDF Processing**: Supports searchable + OCR (scanned) PDFs safely
2. **File Uploads**: UUID-renamed, temporary storage, auto-cleanup
3. **Data Persistence**: JSON-based, local storage, graceful corruption handling
4. **Model Isolation**: Isolation Forest for outlier detection (no sensitive data leakage)
5. **Flask Debug**: Disabled in production (render.yaml uses gunicorn)

## 📈 Performance Optimization

- **Feature Engineering**: 8D feature vectors (efficient computation)
- **Model Caching**: Isolation Forest pickled after training
- **Batch Processing**: Multi-transaction analysis support
- **History Pagination**: JSON-based with efficient queries
- **Lazy Loading**: Templates only load needed data

---

**FraudLens AI** - Real-Time Financial Fraud Detection System for Indian Banks
*Production-Grade Flask + ML Architecture*
