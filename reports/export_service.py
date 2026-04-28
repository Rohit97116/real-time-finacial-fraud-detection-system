import os
import uuid
from textwrap import shorten

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_csv_report(df, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename = f"fraud_report_{uuid.uuid4().hex[:8]}.csv"
    path = os.path.join(output_dir, filename)
    df.to_csv(path, index=False)
    return filename


def export_pdf_report(summary: dict, flagged_df, output_dir: str, customer_name: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename = f"fraud_report_{uuid.uuid4().hex[:8]}.pdf"
    path = os.path.join(output_dir, filename)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Financial Fraud Detection Report")
    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Customer: {customer_name}")
    y -= 20
    c.drawString(40, y, f"Total Transactions: {summary.get('total_txn', 0)}")
    y -= 16
    c.drawString(40, y, f"Flagged Transactions: {summary.get('flagged_txn', 0)}")
    y -= 16
    c.drawString(40, y, f"Average Risk Score: {summary.get('avg_risk', 0):.2f}")
    y -= 26

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Flagged Transaction Preview")
    y -= 18

    c.setFont("Helvetica", 9)
    for _, row in flagged_df.head(30).iterrows():
        desc = shorten(str(row.get("description", "")), width=38, placeholder="...")
        line = (
            f"{row.get('date', '')} | {desc} | "
            f"INR {float(row.get('amount', 0.0)):.2f} | "
            f"{row.get('risk_level', '')}"
        )
        c.drawString(40, y, line)
        y -= 12
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 40

    c.save()
    return filename
