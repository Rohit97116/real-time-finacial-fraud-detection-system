import pandas as pd

def detect_fraud(df):
    # Safety check
    if "Amount" not in df.columns:
        df["Fraud_Flag"] = "Normal"
        return df

    # Ensure Amount is numeric (DO NOT replace NaN with 0)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    # Initialize fraud flag
    df["Fraud_Flag"] = "Normal"

    # Work only with valid (non-null, >0) amounts
    valid_mask = df["Amount"].notna() & (df["Amount"] > 0)
    valid_df = df.loc[valid_mask]

    # ---------------- RULE 1 ----------------
    # Duplicate transactions (Date + Amount + Description)
    duplicates = df.duplicated(
        subset=["Date", "Amount", "Description"],
        keep=False
    )

    df.loc[duplicates, "Fraud_Flag"] = "Possible Duplicate Transaction"

    # ---------------- RULE 2 ----------------
    # High-value transactions (3× mean of valid amounts)
    if not valid_df.empty:
        high_value_threshold = valid_df["Amount"].mean() * 3

        df.loc[
            df["Amount"] > high_value_threshold,
            "Fraud_Flag"
        ] = "Unusually High Amount"

    # ---------------- RULE 3 ----------------
    # Repeated same-amount transactions (ignore NaN / zero)
    repeated_amounts = (
        valid_df.groupby("Amount")
        .size()
    )

    suspicious_amounts = repeated_amounts[
        repeated_amounts >= 3
    ].index

    df.loc[
        df["Amount"].isin(suspicious_amounts),
        "Fraud_Flag"
    ] = "Repeated Amount Transactions"

    return df
