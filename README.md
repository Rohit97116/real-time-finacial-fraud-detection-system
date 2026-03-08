# FraudLens AI - Bank Transaction Fraud Analysis (India)

FraudLens AI is an ML-powered Flask web application that analyzes Indian bank statement PDFs, detects suspicious transactions, and generates downloadable reports.

## Key Features

- Single-month analysis (upload 1 PDF + month tag)
- Multi-month analysis (upload multiple PDFs in one run)
- Previous history combined analysis (customer + selected months)
- Optional merge of current run with customer history data
- Flagged transactions table + full serial-order table
- Visual report dashboard (charts)
- CSV and PDF report download
- Analysis history with quick access to past reports

## Tech Stack

- Python, Flask
- Pandas, NumPy, scikit-learn
- HTML/CSS/JS templates (dark UI)
- Local JSON-based history persistence

## Project Structure

```text
app.py
services/
  feature_service.py
  fraud_service.py
  history_service.py
  model_service.py
  pdf_parser_service.py
reports/
  export_service.py
Templates/
statics/
```

## Local Setup

### 1) Clone repo

```bash
git clone <your-repo-url>
cd "real time finacial fraud detection system"
```

### 2) Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run app

```bash
python app.py
```

Open: `http://127.0.0.1:5000`

## OCR/Parser Requirements (for scanned PDFs)

For scanned bank statements, install:

- Tesseract OCR
- Poppler (for PDF image conversion)

Then set environment variables (Windows):

```powershell
setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
setx POPPLER_PATH "C:\tools\poppler\Library\bin"
```

Restart terminal after setting variables.

## Workflow Modes

### 1) Single-Month Analysis
- Enter profile details
- Select statement month
- Upload one PDF
- Optional: merge with history months

### 2) Multiple-Month Analysis
- Enter profile details
- Upload multiple PDFs
- Optional: merge with history months

### 3) Previous Combined Analysis
- Enter customer name
- Enter month list (e.g. `2026-01, 2026-02`)
- System combines available months and informs missing months

## Outputs

- Fraud summary KPIs
- Flagged transactions table
- Full transactions in serial order
- Visual charts report
- Downloadable CSV and PDF

## Deployment

This project includes deployment files:

- `render.yaml`
- `Dockerfile`
- `DEPLOY_GITHUB_RENDER.md`

Use GitHub + Render for public hosting.

## Notes

- Currency format is INR.
- History is stored in `data/analysis_history.json`.
- Uploaded raw files and generated reports are ignored in Git using `.gitignore`.

## License

Use your preferred license (MIT recommended for academic demo projects).
