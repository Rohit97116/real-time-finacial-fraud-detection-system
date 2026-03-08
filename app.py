import json
import os
import re
import uuid
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from reports.export_service import export_csv_report, export_pdf_report
from services.fraud_service import analyze_with_ml
from services.history_service import append_history_entry, load_history_entries
from services.pdf_parser_service import parse_bank_statement

app = Flask(__name__, template_folder="Templates", static_folder="statics")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024  # 15 MB

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"
ALLOWED_EXTENSIONS = {"pdf"}
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

MODE_LABELS = {
    "single": "Single-Month Analysis",
    "single_plus_history": "Single-Month + History Merge",
    "multi": "Multiple-Month Analysis",
    "multi_plus_history": "Multiple-Month + History Merge",
    "history_combined": "Previous Combined Analysis",
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def to_float(value, default=0.0):
    try:
        parsed = float(value)
        if pd.isna(parsed):
            return default
        return parsed
    except (TypeError, ValueError):
        return default


def format_inr(value) -> str:
    value = to_float(value, 0.0)
    sign = "-" if value < 0 else ""
    value = abs(value)
    integer, decimal = f"{value:.2f}".split(".")

    if len(integer) > 3:
        last_three = integer[-3:]
        rest = integer[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        integer = ",".join(parts + [last_three])

    return f"{sign}INR {integer}.{decimal}"


def normalize_customer_name(name: str) -> str:
    return " ".join((name or "").strip().lower().split())


def normalize_month_token(token: str) -> str:
    raw = (token or "").strip()
    if MONTH_PATTERN.match(raw):
        return raw

    for pattern in ("%b %Y", "%B %Y", "%b-%Y", "%B-%Y", "%m/%Y", "%m-%Y"):
        try:
            return datetime.strptime(raw, pattern).strftime("%Y-%m")
        except ValueError:
            continue
    return ""


def parse_month_list(raw_value: str) -> list[str]:
    text = (raw_value or "").strip()
    if not text:
        return []

    month_tokens = re.findall(r"\b\d{4}-(?:0[1-9]|1[0-2])\b", text)
    if not month_tokens:
        raw_parts = re.split(r"[,;\n|]+", text)
        for part in raw_parts:
            token = normalize_month_token(part)
            if token:
                month_tokens.append(token)

    deduped = []
    seen = set()
    for token in month_tokens:
        if token not in seen:
            seen.add(token)
            deduped.append(token)
    return sorted(deduped)


def month_label(month_token: str) -> str:
    token = normalize_month_token(month_token)
    if not token:
        return month_token
    return datetime.strptime(token, "%Y-%m").strftime("%b %Y")


def month_list_label(month_tokens: list[str]) -> str:
    if not month_tokens:
        return "-"
    return ", ".join(month_label(token) for token in month_tokens)


def infer_months_from_df(df: pd.DataFrame) -> list[str]:
    if df.empty or "date" not in df.columns:
        return []
    parsed = pd.to_datetime(df["date"], errors="coerce")
    months = parsed.dt.strftime("%Y-%m").dropna().unique().tolist()
    return sorted(set(months))


def infer_entry_months(entry: dict) -> list[str]:
    months = []

    covered = entry.get("covered_months", [])
    if isinstance(covered, list):
        for raw in covered:
            token = normalize_month_token(str(raw))
            if token:
                months.append(token)

    if not months:
        statement_month = normalize_month_token(str(entry.get("statement_month", "")))
        if statement_month:
            months.append(statement_month)

    return sorted(set(months))


def month_range_label(month_tokens: list[str]) -> str:
    if not month_tokens:
        return ""
    if len(month_tokens) == 1:
        return month_tokens[0]
    return f"{month_tokens[0]} to {month_tokens[-1]}"


def build_profile_from_form(form_data) -> dict:
    return {
        "name": form_data.get("name", "").strip(),
        "income": to_float(form_data.get("income"), 0.0),
        "savings": to_float(form_data.get("savings"), 0.0),
        "avg_daily": to_float(form_data.get("avg_daily"), 0.0),
        "avg_weekly": to_float(form_data.get("avg_weekly"), 0.0),
        "avg_weekend": to_float(form_data.get("avg_weekend"), 0.0),
        "avg_monthly": to_float(form_data.get("avg_monthly"), 0.0),
    }


def normalize_analyzed_frame(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = [
        "date",
        "description",
        "reference",
        "debit",
        "credit",
        "balance",
        "channel",
        "amount",
        "risk_score",
        "risk_level",
        "fraud_flag",
        "reason",
    ]
    for col in required_cols:
        if col not in df.columns:
            if col in {"debit", "credit", "balance", "amount", "risk_score"}:
                df[col] = 0.0
            elif col == "fraud_flag":
                df[col] = "Normal"
            elif col == "risk_level":
                df[col] = "Low"
            elif col == "channel":
                df[col] = "OTHER"
            elif col == "reason":
                df[col] = "No strong anomaly signals"
            else:
                df[col] = ""

    for col in ["debit", "credit", "balance", "amount", "risk_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    for col in ["date", "description", "reference", "channel", "risk_level", "fraud_flag", "reason"]:
        df[col] = df[col].fillna("").astype(str).replace({"nan": "", "None": ""})

    df["fraud_flag"] = df["fraud_flag"].replace({"": "Normal"})
    df["risk_level"] = df["risk_level"].replace({"": "Low"})
    df["reason"] = df["reason"].replace({"": "No strong anomaly signals"})

    return df


def build_summary_from_analyzed_df(analyzed_df: pd.DataFrame) -> dict:
    risk_mean = to_float(pd.to_numeric(analyzed_df["risk_score"], errors="coerce").mean(), 0.0)
    return {
        "total_txn": int(len(analyzed_df)),
        "flagged_txn": int((analyzed_df["fraud_flag"] == "Flagged").sum()),
        "total_debit": float(pd.to_numeric(analyzed_df["debit"], errors="coerce").fillna(0.0).sum()),
        "total_credit": float(pd.to_numeric(analyzed_df["credit"], errors="coerce").fillna(0.0).sum()),
        "avg_risk": risk_mean,
    }


def build_result_payload(analyzed_df: pd.DataFrame):
    ordered_df = analyzed_df.reset_index(drop=True).copy()
    ordered_df["sr_no"] = ordered_df.index + 1

    display_columns = [
        "sr_no",
        "date",
        "description",
        "channel",
        "debit",
        "credit",
        "balance",
        "amount",
        "risk_score",
        "risk_level",
        "fraud_flag",
        "reason",
    ]

    display_df = ordered_df[display_columns].copy()
    for col in ["debit", "credit", "balance", "amount"]:
        display_df[col] = display_df[col].apply(format_inr)
    display_df["date"] = display_df["date"].astype(str)
    display_df["risk_score"] = pd.to_numeric(display_df["risk_score"], errors="coerce").fillna(0.0).round(2)

    all_transactions = display_df.to_dict(orient="records")
    flagged_transactions = [row for row in all_transactions if row["fraud_flag"] == "Flagged"]
    return display_columns, all_transactions, flagged_transactions


def parse_uploaded_statement(pdf_file):
    if not pdf_file or not pdf_file.filename:
        raise ValueError("Please upload a PDF bank statement.")

    if not allowed_file(pdf_file.filename):
        raise ValueError("Only PDF files are supported.")

    safe_name = secure_filename(pdf_file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    pdf_path = os.path.join(UPLOAD_FOLDER, unique_name)
    pdf_file.save(pdf_path)

    try:
        txn_df = parse_bank_statement(pdf_path)
        return txn_df, safe_name
    finally:
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except OSError:
            pass


def parse_multiple_uploaded_statements(pdf_files):
    source_files = []
    frames = []

    for item in pdf_files:
        if not item or not item.filename:
            continue
        txn_df, safe_name = parse_uploaded_statement(item)
        source_files.append(safe_name)
        if not txn_df.empty:
            frames.append(txn_df)

    if not source_files:
        raise ValueError("Please upload at least one PDF bank statement.")
    if not frames:
        raise ValueError("No transactions could be extracted from the uploaded statements.")

    combined_df = pd.concat(frames, ignore_index=True)
    combined_df = combined_df.sort_values(by="date", kind="stable").reset_index(drop=True)
    return combined_df, source_files


def combine_and_dedupe_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    usable_frames = []
    for frame in frames:
        if frame is None or frame.empty:
            continue
        usable_frames.append(normalize_analyzed_frame(frame.copy()))

    if not usable_frames:
        return pd.DataFrame()

    combined_df = pd.concat(usable_frames, ignore_index=True)
    dedupe_cols = [
        col
        for col in ["date", "description", "reference", "debit", "credit", "balance", "amount", "fraud_flag", "reason"]
        if col in combined_df.columns
    ]
    if dedupe_cols:
        combined_df = combined_df.drop_duplicates(subset=dedupe_cols, keep="first")

    if "date" in combined_df.columns:
        combined_df = combined_df.sort_values(by="date", kind="stable")

    return combined_df.reset_index(drop=True)


def load_history_frames_for_customer(customer_name: str, requested_months: list[str] | None = None) -> dict:
    result = {
        "customer_found": False,
        "requested_months": sorted(set(requested_months or [])),
        "available_months": [],
        "used_months": [],
        "missing_months": [],
        "frames": [],
        "source_files": [],
    }

    target_customer = normalize_customer_name(customer_name)
    if not target_customer:
        return result

    entries = load_history_entries()
    customer_entries = [
        row for row in entries if normalize_customer_name(str(row.get("customer_name", ""))) == target_customer
    ]
    if not customer_entries:
        return result

    result["customer_found"] = True
    available_months = sorted({month for row in customer_entries for month in infer_entry_months(row)})
    result["available_months"] = available_months

    desired_months = result["requested_months"] or available_months
    result["requested_months"] = desired_months
    if not desired_months:
        return result

    month_to_entry = {}
    for month in desired_months:
        for entry in customer_entries:
            csv_name = secure_filename(str(entry.get("csv_file", "")))
            csv_path = os.path.join(REPORT_FOLDER, csv_name)
            if not csv_name or not os.path.exists(csv_path):
                continue
            if month in infer_entry_months(entry):
                month_to_entry[month] = entry
                break

    result["used_months"] = sorted(month_to_entry.keys())
    result["missing_months"] = sorted([month for month in desired_months if month not in month_to_entry])

    entry_to_months = {}
    entry_lookup = {}
    for month, entry in month_to_entry.items():
        entry_key = str(entry.get("analysis_id", f'{entry.get("csv_file", "")}:{month}'))
        entry_lookup[entry_key] = entry
        entry_to_months.setdefault(entry_key, set()).add(month)

    failed_months = []
    frames = []
    source_files = []
    for entry_key, matched_months in entry_to_months.items():
        entry = entry_lookup[entry_key]
        csv_name = secure_filename(str(entry.get("csv_file", "")))
        csv_path = os.path.join(REPORT_FOLDER, csv_name)

        try:
            frame = pd.read_csv(csv_path)
        except Exception:
            app.logger.exception("Unable to load historical CSV report for months %s", sorted(matched_months))
            failed_months.extend(sorted(matched_months))
            continue

        frame = normalize_analyzed_frame(frame)
        frame["source_month"] = ", ".join(sorted(matched_months))
        frames.append(frame)

        source_statement = str(entry.get("source_statement", csv_name)).strip()
        source_files.append(source_statement or csv_name)

    if failed_months:
        failed_set = set(failed_months)
        result["used_months"] = sorted(set(result["used_months"]) - failed_set)
        result["missing_months"] = sorted(set(result["missing_months"]).union(failed_set))

    result["frames"] = frames
    result["source_files"] = sorted(set(source_files))
    return result


def build_summary_view(summary: dict) -> dict:
    return {
        "total_txn": int(summary.get("total_txn", 0)),
        "flagged_txn": int(summary.get("flagged_txn", 0)),
        "total_debit": format_inr(summary.get("total_debit", 0.0)),
        "total_credit": format_inr(summary.get("total_credit", 0.0)),
        "avg_risk": f'{to_float(summary.get("avg_risk"), 0.0):.2f}',
    }


def store_history_entry(
    customer_name: str,
    summary: dict,
    csv_file: str,
    pdf_file: str,
    source_files: list[str],
    analysis_mode: str,
    statement_month: str = "",
    covered_months: list[str] | None = None,
):
    covered_months = covered_months or []
    source_statement = ", ".join(source_files[:2])
    if len(source_files) > 2:
        source_statement += f" (+{len(source_files) - 2} more)"
    if not source_statement:
        source_statement = "-"

    history_entry = {
        "analysis_id": uuid.uuid4().hex[:12],
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_name": customer_name or "Unknown",
        "source_statement": source_statement,
        "source_files": source_files,
        "analysis_mode": analysis_mode,
        "statement_month": statement_month,
        "covered_months": covered_months,
        "total_txn": int(summary.get("total_txn", 0)),
        "flagged_txn": int(summary.get("flagged_txn", 0)),
        "total_debit": float(summary.get("total_debit", 0.0)),
        "total_credit": float(summary.get("total_credit", 0.0)),
        "avg_risk": float(to_float(summary.get("avg_risk"), 0.0)),
        "csv_file": csv_file,
        "pdf_file": pdf_file,
    }
    append_history_entry(history_entry)


def render_analysis_result(
    customer_name: str,
    analyzed_df: pd.DataFrame,
    summary: dict,
    csv_file: str,
    pdf_file: str,
    mode_label: str,
    scope_label: str = "",
    notes: list[str] | None = None,
):
    display_columns, all_transactions, flagged_transactions = build_result_payload(analyzed_df)
    summary_view = build_summary_view(summary)
    return render_template(
        "result.html",
        customer_name=customer_name,
        summary=summary_view,
        columns=display_columns,
        flagged_transactions=flagged_transactions,
        all_transactions=all_transactions,
        csv_file=csv_file,
        pdf_file=pdf_file,
        analysis_mode_label=mode_label,
        analysis_scope=scope_label,
        analysis_notes=notes or [],
    )


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/details")
def details():
    return render_template("analysis_mode.html")


@app.route("/details/single")
def details_single():
    return render_template("details_single.html")


@app.route("/details/multi")
def details_multi():
    return render_template("details_multi.html")


@app.route("/details/previous")
def details_previous():
    rows = load_history_entries()
    customer_options = sorted(
        {str(row.get("customer_name", "")).strip() for row in rows if str(row.get("customer_name", "")).strip()}
    )
    month_options = sorted({month for row in rows for month in infer_entry_months(row)})
    return render_template(
        "combined_history.html",
        customer_options=customer_options,
        month_options=month_options,
    )


@app.route("/analyze", methods=["POST"])
def analyze_legacy():
    flash("The workflow has been upgraded. Please choose Single-Month or Multiple-Month analysis mode.")
    return redirect(url_for("details"))


@app.route("/analyze/single", methods=["POST"])
def analyze_single():
    profile = build_profile_from_form(request.form)
    statement_month = normalize_month_token(request.form.get("statement_month", ""))
    if not statement_month:
        flash("Please select a valid statement month (YYYY-MM).")
        return redirect(url_for("details_single"))

    include_history = request.form.get("include_history") == "1"
    requested_history_months = parse_month_list(request.form.get("history_months", ""))
    pdf_file = request.files.get("statement")

    try:
        txn_df, source_file = parse_uploaded_statement(pdf_file)
        if txn_df.empty:
            flash("No transactions could be extracted from this statement. Please try another file.")
            return redirect(url_for("details_single"))

        analyzed_df, summary = analyze_with_ml(txn_df, profile)
        analyzed_df = normalize_analyzed_frame(analyzed_df)

        notes = [f"Selected statement month: {month_label(statement_month)}."]
        current_months = infer_months_from_df(analyzed_df)
        if current_months:
            notes.append(f"Detected transaction months in uploaded statement: {month_list_label(current_months)}.")

        used_history_months = []
        if include_history:
            history_bundle = load_history_frames_for_customer(
                profile["name"],
                requested_history_months if requested_history_months else None,
            )
            if requested_history_months:
                notes.append(f"Requested history months: {month_list_label(requested_history_months)}.")
            elif history_bundle["available_months"]:
                notes.append(
                    "History merge enabled without month filter. Using all available months for this customer."
                )

            if not history_bundle["customer_found"]:
                notes.append("No existing history was found for this customer. Result includes uploaded statement only.")
            elif not history_bundle["frames"]:
                if history_bundle["requested_months"]:
                    notes.append(
                        f"No usable history reports found for: {month_list_label(history_bundle['requested_months'])}."
                    )
                else:
                    notes.append("History reports are present but could not be loaded. Using uploaded statement only.")
            else:
                history_df = combine_and_dedupe_frames(history_bundle["frames"])
                combined_df = combine_and_dedupe_frames([analyzed_df, history_df])
                if not combined_df.empty:
                    analyzed_df = normalize_analyzed_frame(combined_df)
                    summary = build_summary_from_analyzed_df(analyzed_df)
                    used_history_months = history_bundle["used_months"]
                    notes.append(f"Included history months: {month_list_label(used_history_months)}.")
                    if history_bundle["missing_months"]:
                        notes.append(
                            f"History data not available for: {month_list_label(history_bundle['missing_months'])}. "
                            "Generated result uses available months only."
                        )

        flagged_df = analyzed_df[analyzed_df["fraud_flag"] == "Flagged"].copy()
        csv_file = export_csv_report(analyzed_df, REPORT_FOLDER)
        pdf_file_name = export_pdf_report(summary, flagged_df, REPORT_FOLDER, profile["name"])

        detected_months = infer_months_from_df(analyzed_df)
        covered_months = sorted(set(detected_months + [statement_month] + used_history_months))
        statement_scope_value = month_range_label(covered_months) or statement_month

        mode_key = "single_plus_history" if include_history and used_history_months else "single"
        if mode_key == "single_plus_history":
            scope_label = f"Uploaded Month + History: {month_list_label(covered_months)}"
            source_items = [source_file, f"History months: {month_list_label(used_history_months)}"]
        else:
            scope_label = f"Statement Month: {month_label(statement_month)}"
            source_items = [source_file]

        store_history_entry(
            customer_name=profile["name"],
            summary=summary,
            csv_file=csv_file,
            pdf_file=pdf_file_name,
            source_files=source_items,
            analysis_mode=mode_key,
            statement_month=statement_scope_value,
            covered_months=covered_months,
        )

        return render_analysis_result(
            customer_name=profile["name"],
            analyzed_df=analyzed_df,
            summary=summary,
            csv_file=csv_file,
            pdf_file=pdf_file_name,
            mode_label=MODE_LABELS[mode_key],
            scope_label=scope_label,
            notes=notes,
        )
    except ValueError as exc:
        flash(str(exc))
        return redirect(url_for("details_single"))
    except Exception:
        app.logger.exception("Analysis error during single-month processing")
        flash("Analysis failed while processing the statement. Please verify the input file and try again.")
        return redirect(url_for("details_single"))


@app.route("/analyze/multi", methods=["POST"])
def analyze_multi():
    profile = build_profile_from_form(request.form)
    include_history = request.form.get("include_history") == "1"
    requested_history_months = parse_month_list(request.form.get("history_months", ""))
    pdf_files = request.files.getlist("statements")

    if not pdf_files:
        flash("Please upload at least one PDF bank statement.")
        return redirect(url_for("details_multi"))

    try:
        txn_df, source_files = parse_multiple_uploaded_statements(pdf_files)
        analyzed_df, summary = analyze_with_ml(txn_df, profile)
        analyzed_df = normalize_analyzed_frame(analyzed_df)

        notes = [f"Combined analysis generated from {len(source_files)} uploaded statement file(s)."]
        current_months = infer_months_from_df(analyzed_df)
        if current_months:
            notes.append(f"Detected transaction months in uploaded files: {month_list_label(current_months)}.")

        used_history_months = []

        if include_history:
            history_bundle = load_history_frames_for_customer(
                profile["name"],
                requested_history_months if requested_history_months else None,
            )
            if requested_history_months:
                notes.append(f"Requested history months: {month_list_label(requested_history_months)}.")
            elif history_bundle["available_months"]:
                notes.append(
                    "History merge enabled without month filter. Using all available months for this customer."
                )

            if not history_bundle["customer_found"]:
                notes.append("No existing history was found for this customer. Result includes uploaded files only.")
            elif not history_bundle["frames"]:
                if history_bundle["requested_months"]:
                    notes.append(
                        f"No usable history reports found for: {month_list_label(history_bundle['requested_months'])}."
                    )
                else:
                    notes.append("History reports are present but could not be loaded. Using uploaded files only.")
            else:
                history_df = combine_and_dedupe_frames(history_bundle["frames"])
                combined_df = combine_and_dedupe_frames([analyzed_df, history_df])
                if not combined_df.empty:
                    analyzed_df = normalize_analyzed_frame(combined_df)
                    summary = build_summary_from_analyzed_df(analyzed_df)
                    used_history_months = history_bundle["used_months"]
                    notes.append(f"Included history months: {month_list_label(used_history_months)}.")
                    if history_bundle["missing_months"]:
                        notes.append(
                            f"History data not available for: {month_list_label(history_bundle['missing_months'])}. "
                            "Generated result uses available months only."
                        )

        flagged_df = analyzed_df[analyzed_df["fraud_flag"] == "Flagged"].copy()
        csv_file = export_csv_report(analyzed_df, REPORT_FOLDER)
        pdf_file_name = export_pdf_report(summary, flagged_df, REPORT_FOLDER, profile["name"])

        covered_months = sorted(set(infer_months_from_df(analyzed_df) + used_history_months))
        statement_month = month_range_label(covered_months)

        mode_key = "multi_plus_history" if include_history and used_history_months else "multi"
        if mode_key == "multi_plus_history":
            scope_label = f"Uploaded Files + History Months: {month_list_label(covered_months)}"
            merged_sources = source_files + [f"History months: {month_list_label(used_history_months)}"]
        else:
            scope_label = f"Files Processed: {len(source_files)}"
            merged_sources = source_files

        store_history_entry(
            customer_name=profile["name"],
            summary=summary,
            csv_file=csv_file,
            pdf_file=pdf_file_name,
            source_files=merged_sources,
            analysis_mode=mode_key,
            statement_month=statement_month,
            covered_months=covered_months,
        )

        return render_analysis_result(
            customer_name=profile["name"],
            analyzed_df=analyzed_df,
            summary=summary,
            csv_file=csv_file,
            pdf_file=pdf_file_name,
            mode_label=MODE_LABELS[mode_key],
            scope_label=scope_label,
            notes=notes,
        )
    except ValueError as exc:
        flash(str(exc))
        return redirect(url_for("details_multi"))
    except Exception:
        app.logger.exception("Analysis error during multi-month processing")
        flash("Analysis failed while processing uploaded statements. Please verify the input files and try again.")
        return redirect(url_for("details_multi"))


@app.route("/analyze/previous", methods=["POST"])
def analyze_previous():
    customer_name = request.form.get("customer_name", "").strip()
    requested_months = parse_month_list(request.form.get("months", ""))

    if not customer_name:
        flash("Please enter the customer name.")
        return redirect(url_for("details_previous"))
    if not requested_months:
        flash("Please enter at least one valid month in YYYY-MM format.")
        return redirect(url_for("details_previous"))

    history_bundle = load_history_frames_for_customer(customer_name, requested_months)
    if not history_bundle["customer_found"]:
        flash("No history entries were found for the selected customer.")
        return redirect(url_for("details_previous"))

    usable_months = history_bundle["used_months"]
    missing_months = history_bundle["missing_months"]

    if not usable_months:
        flash(
            f"No selected month data is available for this customer. Missing months: {month_list_label(missing_months)}."
        )
        return redirect(url_for("details_previous"))

    if not history_bundle["frames"]:
        flash("Selected history entries could not be loaded for combined analysis.")
        return redirect(url_for("details_previous"))

    combined_df = combine_and_dedupe_frames(history_bundle["frames"])
    if combined_df.empty:
        flash("Selected history entries contain no usable transactions for combined analysis.")
        return redirect(url_for("details_previous"))

    summary = build_summary_from_analyzed_df(combined_df)
    flagged_df = combined_df[combined_df["fraud_flag"] == "Flagged"].copy()
    csv_file = export_csv_report(combined_df, REPORT_FOLDER)
    pdf_file_name = export_pdf_report(summary, flagged_df, REPORT_FOLDER, customer_name)

    notes = [f"Requested months: {month_list_label(requested_months)}."]
    notes.append(f"Used months: {month_list_label(usable_months)}.")
    if missing_months:
        notes.append(
            f"Data for {month_list_label(missing_months)} is not available in history. "
            "Combined analysis was generated using available months only."
        )

    store_history_entry(
        customer_name=customer_name,
        summary=summary,
        csv_file=csv_file,
        pdf_file=pdf_file_name,
        source_files=history_bundle["source_files"],
        analysis_mode="history_combined",
        statement_month=month_range_label(usable_months),
        covered_months=usable_months,
    )

    return render_analysis_result(
        customer_name=customer_name,
        analyzed_df=combined_df,
        summary=summary,
        csv_file=csv_file,
        pdf_file=pdf_file_name,
        mode_label=MODE_LABELS["history_combined"],
        scope_label=f"Combined Historical Months: {month_list_label(usable_months)}",
        notes=notes,
    )


@app.route("/history")
def history():
    rows = load_history_entries()
    history_rows = []

    for row in rows:
        item = dict(row)
        csv_file = item.get("csv_file", "")
        pdf_file = item.get("pdf_file", "")

        months = infer_entry_months(item)
        item["analysis_mode_label"] = MODE_LABELS.get(str(item.get("analysis_mode", "")).strip(), "Standard Analysis")
        item["months_display"] = month_list_label(months)
        item["total_debit_fmt"] = format_inr(to_float(item.get("total_debit"), 0.0))
        item["total_credit_fmt"] = format_inr(to_float(item.get("total_credit"), 0.0))
        item["avg_risk_fmt"] = f'{to_float(item.get("avg_risk"), 0.0):.2f}'
        item["csv_available"] = bool(csv_file) and os.path.exists(os.path.join(REPORT_FOLDER, csv_file))
        item["pdf_available"] = bool(pdf_file) and os.path.exists(os.path.join(REPORT_FOLDER, pdf_file))
        history_rows.append(item)

    return render_template("history.html", history_rows=history_rows)


@app.route("/report/<filename>")
def report_dashboard(filename):
    safe_name = secure_filename(filename)
    csv_path = os.path.join(REPORT_FOLDER, safe_name)
    if not os.path.exists(csv_path):
        flash("The requested report file could not be found.")
        return redirect(url_for("history"))

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        app.logger.exception("Unable to load report data for %s", safe_name)
        flash("Unable to load report data. The file may be corrupted or unreadable.")
        return redirect(url_for("history"))

    if df.empty:
        flash("The selected report has no data to visualize.")
        return redirect(url_for("history"))

    pdf_file = secure_filename(request.args.get("pdf", ""))
    customer_name = request.args.get("customer", "Customer")

    if "amount" in df.columns:
        amount_series = pd.to_numeric(df["amount"], errors="coerce").dropna()
    else:
        amount_series = pd.Series(dtype=float)

    if "channel" in df.columns:
        channel_counts = df["channel"].fillna("OTHER").astype(str).value_counts().to_dict()
    else:
        channel_counts = {"OTHER": int(len(df))}

    if "risk_level" in df.columns:
        risk_counts = df["risk_level"].fillna("Unknown").astype(str).value_counts().to_dict()
    else:
        risk_counts = {"Unknown": int(len(df))}

    if "fraud_flag" in df.columns:
        flag_counts = df["fraud_flag"].fillna("Unknown").astype(str).value_counts().to_dict()
    else:
        flag_counts = {"Unknown": int(len(df))}

    def numeric_series(column_name: str):
        if column_name in df.columns:
            return pd.to_numeric(df[column_name], errors="coerce").fillna(0)
        return pd.Series([0.0] * len(df))

    avg_risk = to_float(numeric_series("risk_score").mean(), 0.0)
    summary = {
        "total_txn": int(len(df)),
        "total_debit": format_inr(numeric_series("debit").sum()),
        "total_credit": format_inr(numeric_series("credit").sum()),
        "flagged_txn": int(flag_counts.get("Flagged", 0)),
        "avg_risk": f"{avg_risk:.2f}",
    }

    data_payload = {
        "channel_labels": list(channel_counts.keys()),
        "channel_values": list(channel_counts.values()),
        "risk_labels": list(risk_counts.keys()),
        "risk_values": list(risk_counts.values()),
        "amount_values": amount_series.round(2).tolist(),
    }

    return render_template(
        "report.html",
        customer_name=customer_name,
        csv_file=safe_name,
        pdf_file=pdf_file,
        summary=summary,
        chart_data=json.dumps(data_payload),
    )


@app.route("/download/<filename>")
def download_report(filename):
    safe_name = secure_filename(filename)
    file_path = os.path.join(REPORT_FOLDER, safe_name)
    if not os.path.exists(file_path):
        flash("The requested report file could not be found.")
        if request.referrer:
            parsed_ref = urlparse(request.referrer)
            if parsed_ref.path == url_for("history"):
                return redirect(url_for("history"))
            if parsed_ref.path.startswith("/report/"):
                safe_target = parsed_ref.path
                if parsed_ref.query:
                    safe_target += f"?{parsed_ref.query}"
                return redirect(safe_target)
        return redirect(url_for("details"))
    return send_file(file_path, as_attachment=True)


@app.errorhandler(RequestEntityTooLarge)
def handle_oversized_upload(_error):
    flash("Uploaded file is too large. Please upload PDF files up to 15 MB.")
    return redirect(url_for("details"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
