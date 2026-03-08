import re
import pandas as pd

from table_parser import extract_transactions_from_pdf
from pdf_reader import extract_text_from_pdf
from transaction_parser import parse_transactions


def _detect_channel(description: str) -> str:
    text = str(description).lower()
    if "upi" in text:
        return "UPI"
    if "imps" in text:
        return "IMPS"
    if "neft" in text:
        return "NEFT"
    if "rtgs" in text:
        return "RTGS"
    if "atm" in text:
        return "ATM"
    if "pos" in text:
        return "POS"
    if "nach" in text:
        return "NACH"
    return "OTHER"


def _extract_reference(description: str) -> str:
    pattern = r"(UTR[:\s-]*[A-Z0-9]+|RRN[:\s-]*[0-9]+|REF[:\s-]*[A-Z0-9]+)"
    match = re.search(pattern, str(description), flags=re.IGNORECASE)
    return match.group(0).strip() if match else ""


def _is_non_transaction_row(description: str) -> bool:
    text = str(description).lower().strip()
    if not text:
        return True

    non_txn_keywords = [
        "opening balance",
        "closing balance",
        "brought forward",
        "carried forward",
        "balance b/f",
        "balance c/f",
        "transaction details",
        "cheque/reference",
        "statement period",
    ]
    if any(keyword in text for keyword in non_txn_keywords):
        return True

    # Avoid broad "total" matching that can hide legitimate merchant descriptions.
    total_patterns = [
        r"^total$",
        r"^totals$",
        r"^grand total.*$",
        r"^total credits?.*$",
        r"^total debits?.*$",
        r"^total transactions?.*$",
    ]
    return any(re.match(pattern, text) for pattern in total_patterns)


def parse_bank_statement(file_path: str) -> pd.DataFrame:
    df = extract_transactions_from_pdf(file_path)

    if df.empty:
        text = extract_text_from_pdf(file_path)
        df = parse_transactions(text)

    rename_map = {
        "Date": "date",
        "Description": "description",
        "Withdrawal": "debit",
        "Withdrawal (Dr.)": "debit",
        "Deposit": "credit",
        "Deposit (Cr.)": "credit",
        "Balance": "balance",
        "Reference": "reference",
        "Ref": "reference",
    }
    df = df.rename(columns=rename_map)

    required_cols = ["date", "description", "reference", "debit", "credit", "balance"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    for col in ["debit", "credit", "balance"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Statements often store debit as negative values; normalize to positive magnitudes.
    df["debit"] = df["debit"].abs()
    df["credit"] = df["credit"].abs()

    def _clean_series_text(series: pd.Series) -> pd.Series:
        return (
            series.fillna("")
            .astype(str)
            .str.strip()
            .replace({"nan": "", "none": "", "None": ""})
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True).dt.date
    df["description"] = _clean_series_text(df["description"])
    df["reference"] = _clean_series_text(df["reference"])

    empty_ref = df["reference"] == ""
    df.loc[empty_ref, "reference"] = df.loc[empty_ref, "description"].apply(_extract_reference)

    df["channel"] = df["description"].apply(_detect_channel)
    df["amount"] = df["debit"].where(df["debit"] > 0, df["credit"])

    non_txn_mask = df["description"].apply(_is_non_transaction_row)
    df = df[(df["amount"] > 0) & (df["date"].notna()) & (~non_txn_mask)].copy()
    df = df.sort_values(by="date", kind="stable").reset_index(drop=True)

    return df[["date", "description", "reference", "debit", "credit", "balance", "channel", "amount"]]
