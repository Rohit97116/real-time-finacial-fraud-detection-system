import re
import pdfplumber
import pandas as pd


def _clean_text(value):
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def _is_header_row(row):
    text = " ".join(_clean_text(cell).lower() for cell in row if cell is not None)
    return "date" in text and ("transaction" in text or "narration" in text or "details" in text)


def _find_index(headers, keywords):
    for idx, header in enumerate(headers):
        if any(keyword in header for keyword in keywords):
            return idx
    return -1


def _extract_from_header_mapped_table(table):
    rows = []
    if not table:
        return rows

    header = [_clean_text(cell).lower() for cell in table[0]]
    if not header:
        return rows

    date_idx = _find_index(header, ["date", "txn date", "transaction date"])
    desc_idx = _find_index(header, ["transaction details", "narration", "description", "particular"])
    ref_idx = _find_index(header, ["reference", "cheque", "chq", "utr", "rrn", "ref"])
    debit_idx = _find_index(header, ["debit", "withdrawal", "dr"])
    credit_idx = _find_index(header, ["credit", "deposit", "cr"])
    balance_idx = _find_index(header, ["balance"])

    if date_idx < 0 or desc_idx < 0:
        return rows

    for row in table[1:]:
        if not row:
            continue

        date_val = _safe_get(row, date_idx)
        desc_val = _safe_get(row, desc_idx)

        if not date_val and not desc_val:
            continue

        rows.append(
            {
                "Date": _clean_text(date_val),
                "Description": _clean_text(desc_val),
                "Ref": _clean_text(_safe_get(row, ref_idx)) if ref_idx >= 0 else "",
                "Withdrawal": safe_float(_safe_get(row, debit_idx)) if debit_idx >= 0 else None,
                "Deposit": safe_float(_safe_get(row, credit_idx)) if credit_idx >= 0 else None,
                "Balance": safe_float(_safe_get(row, balance_idx)) if balance_idx >= 0 else None,
            }
        )

    return rows


def _safe_get(row, idx):
    if idx < 0 or idx >= len(row):
        return None
    return row[idx]


def _extract_from_fixed_width_row(row):
    # Common statement patterns:
    # 1) [Date, Description, Ref, Debit, Credit, Balance]
    # 2) [#, Date, Description, Ref, Debit, Credit, Balance]
    if len(row) >= 7:
        return {
            "Date": _clean_text(row[1]),
            "Description": _clean_text(row[2]),
            "Ref": _clean_text(row[3]),
            "Withdrawal": safe_float(row[4]),
            "Deposit": safe_float(row[5]),
            "Balance": safe_float(row[6]),
        }
    if len(row) >= 6:
        return {
            "Date": _clean_text(row[0]),
            "Description": _clean_text(row[1]),
            "Ref": _clean_text(row[2]),
            "Withdrawal": safe_float(row[3]),
            "Deposit": safe_float(row[4]),
            "Balance": safe_float(row[5]),
        }
    return None


def extract_transactions_from_pdf(file_path):
    all_rows = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                if _is_header_row(table[0]):
                    all_rows.extend(_extract_from_header_mapped_table(table))
                    continue

                for row in table:
                    if not row or _is_header_row(row):
                        continue
                    parsed = _extract_from_fixed_width_row(row)
                    if parsed:
                        all_rows.append(parsed)

    df = pd.DataFrame(all_rows)
    return df


def safe_float(value):
    try:
        if value is None:
            return None

        raw = str(value).strip()
        if raw == "":
            return None

        cleaned = raw.replace(",", "").replace(" ", "")
        cleaned = cleaned.replace("CR", "").replace("DR", "")
        cleaned = cleaned.replace("cr", "").replace("dr", "")
        cleaned = re.sub(r"[^\d\.\-\+]", "", cleaned)

        if cleaned in {"", "-", "+", ".", "-.", "+."}:
            return None

        return float(cleaned)
    except (TypeError, ValueError):
        return None
