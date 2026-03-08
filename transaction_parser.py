import pandas as pd
import re

def parse_transactions(text):
    rows = []
    current_date = "Unknown"
    last_amount = None

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        # Detect date
        date_match = re.search(r"\d{2}\s[A-Za-z]{3}\s\d{4}", line)
        if date_match:
            current_date = date_match.group()
            continue

        # Detect standalone amount line
        amount_match = re.fullmatch(r"\d+\.\d{2}", line)
        if amount_match:
            last_amount = float(line)
            continue

        # Detect transaction line
        if "UPI" in line or "Payment" in line or "MB:" in line:
            description = line

            # Determine type
            if any(w in line.lower() for w in ["sent", "paid", "withdrawal"]):
                withdrawal = last_amount
                deposit = None
            elif any(w in line.lower() for w in ["received", "deposit"]):
                withdrawal = None
                deposit = last_amount
            else:
                withdrawal = None
                deposit = None

            rows.append({
                "Date": current_date,
                "Description": description,
                "Withdrawal (Dr.)": withdrawal,
                "Deposit (Cr.)": deposit,
                "Balance": None  # optional, can be computed later
            })

            last_amount = None

    df = pd.DataFrame(rows)
    return df
