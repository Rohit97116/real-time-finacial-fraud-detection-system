from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from pdf_reader import extract_text_from_pdf
from transaction_parser import parse_transactions
from fraud_detector import detect_fraud
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HELPER FUNCTION ----------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- ROUTES ----------------

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/details")
def details():
    return render_template("details.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    name = request.form.get("name")
    income = request.form.get("income")
    savings = request.form.get("savings")
    pdf_file = request.files.get("statement")

    table_html = ""
    csv_file = None
    filename = ""

    # ---------------- VALIDATION ----------------
    if not pdf_file or pdf_file.filename.strip() == "":
        flash("Please upload a PDF file.")
        return redirect(url_for("details"))

    if not allowed_file(pdf_file.filename):
        flash("Only PDF files are allowed.")
        return redirect(url_for("details"))

    # ---------------- SAVE FILE ----------------
    filename = secure_filename(pdf_file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    pdf_file.save(file_path)

    try:
        # ---------------- STEP 1: EXTRACT TEXT ----------------
        extracted_text = extract_text_from_pdf(file_path)
        print("Extracted text length:", len(extracted_text))

        # ---------------- STEP 2: PARSE TRANSACTIONS ----------------
        df = parse_transactions(extracted_text)

        if df.empty:
            flash("No transactions detected in the uploaded PDF.")
            return redirect(url_for("details"))

        # ---------------- STEP 3: FRAUD DETECTION ----------------
        df = detect_fraud(df)

        # ---------------- STEP 4: SAVE CSV REPORT ----------------
        csv_file = f"fraud_report_{uuid.uuid4().hex[:8]}.csv"
        csv_path = os.path.join(UPLOAD_FOLDER, csv_file)
        df.to_csv(csv_path, index=False)

        # ---------------- STEP 5: HIGHLIGHT FRAUD ROWS ----------------
        def highlight_fraud(row):
            return [
                "background-color: #ffe6e6"
                if row.get("Fraud_Flag") != "Normal"
                else ""
            ] * len(row)

        styled_df = df.style.apply(highlight_fraud, axis=1)

        table_html = styled_df.to_html(
            index=False,
            table_attributes='style="width:100%; border-collapse:collapse;"'
        )

    except Exception as e:
        print("Error during analysis:", e)
        flash("An error occurred while processing the file.")
        return redirect(url_for("details"))

    return render_template(
        "result.html",
        name=name,
        income=income,
        savings=savings,
        file=filename,
        table=table_html,
        csv_file=csv_file
    )


@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found.")
        return redirect(url_for("details"))


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)