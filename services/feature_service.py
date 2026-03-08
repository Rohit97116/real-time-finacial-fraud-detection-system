import pandas as pd


CHANNEL_MAP = {
    "OTHER": 0,
    "UPI": 1,
    "IMPS": 2,
    "NEFT": 3,
    "RTGS": 4,
    "ATM": 5,
    "POS": 6,
    "NACH": 7,
}


def build_feature_frame(txn_df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    df = txn_df.copy()

    income = max(float(profile.get("income", 0.0)), 1.0)
    avg_daily = max(float(profile.get("avg_daily", 0.0)), 1.0)
    avg_monthly = max(float(profile.get("avg_monthly", 0.0)), 1.0)

    df["txn_date"] = pd.to_datetime(df["date"], errors="coerce")
    df["day_of_week"] = df["txn_date"].dt.dayofweek.fillna(0).astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_debit"] = (df["debit"] > 0).astype(int)
    df["channel_code"] = df["channel"].map(CHANNEL_MAP).fillna(0).astype(int)

    df["amount_to_income"] = df["amount"] / income
    df["amount_vs_daily_avg"] = (df["amount"] - avg_daily).abs() / avg_daily
    df["amount_vs_monthly_avg"] = (df["amount"] - avg_monthly).abs() / avg_monthly

    features = df[
        [
            "amount",
            "is_debit",
            "day_of_week",
            "is_weekend",
            "channel_code",
            "amount_to_income",
            "amount_vs_daily_avg",
            "amount_vs_monthly_avg",
        ]
    ].copy()

    return features.fillna(0.0)
