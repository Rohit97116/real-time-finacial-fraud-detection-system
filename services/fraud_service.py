import numpy as np
import pandas as pd

from services.feature_service import build_feature_frame
from services.model_service import score_anomalies


def analyze_with_ml(txn_df: pd.DataFrame, profile: dict):
    df = txn_df.copy().reset_index(drop=True)

    if df.empty:
        return df, {
            "total_txn": 0,
            "flagged_txn": 0,
            "total_debit": 0.0,
            "total_credit": 0.0,
            "avg_risk": 0.0,
        }

    for col in ["debit", "credit", "balance", "amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    features = build_feature_frame(df, profile)
    ml_score, ml_pred = score_anomalies(features)

    df["ml_score"] = (ml_score * 100).round(2)
    df["ml_pred"] = ml_pred

    reasons = [[] for _ in range(len(df))]
    rule_points = np.zeros(len(df), dtype=float)
    strong_hits = np.zeros(len(df), dtype=bool)

    def add_reason(mask, reason_text, points, strong=False):
        idx_list = list(df.index[mask])
        for i in idx_list:
            reasons[i].append(reason_text)
            rule_points[i] += points
            if strong:
                strong_hits[i] = True

    # Strong signal: same date + amount + reference repeated.
    duplicate_ref_mask = (
        df["reference"].ne("")
        & df.duplicated(subset=["date", "reference", "amount"], keep=False)
    )
    add_reason(
        duplicate_ref_mask,
        "Possible duplicate posting (same reference and amount)",
        45,
        strong=True,
    )

    # Medium signal: amount unusually high for the user profile.
    avg_daily = max(float(profile.get("avg_daily", 0.0)), 1.0)
    income = max(float(profile.get("income", 0.0)), 1.0)

    high_threshold = max(avg_daily * 4.0, income * 0.15)
    high_mask = df["amount"] >= high_threshold
    add_reason(high_mask, "Higher than usual amount for this profile", 14)

    very_high_threshold = max(avg_daily * 8.0, income * 0.35)
    very_high_mask = df["amount"] >= very_high_threshold
    add_reason(
        very_high_mask,
        "Very high amount for this profile",
        28,
        strong=True,
    )

    # Soft signal: same debit amount repeated many times on the same day.
    debit_df = df[df["debit"] > 0].copy()
    debit_df["amount_round"] = debit_df["amount"].round(2)
    repeated_groups = (
        debit_df[debit_df["amount_round"] >= 100]
        .groupby(["date", "amount_round"])
        .size()
    )
    suspicious_groups = repeated_groups[repeated_groups >= 3].index

    if len(suspicious_groups) > 0:
        keys = pd.Series(list(zip(df["date"], df["amount"].round(2))), index=df.index)
        repeat_mask = keys.isin(suspicious_groups) & (df["debit"] > 0)
        add_reason(repeat_mask, "Same debit amount repeated several times in one day", 10)

    # Strong signal: running balance math does not reconcile.
    for i in range(1, len(df)):
        prev_balance = df.at[i - 1, "balance"]
        curr_balance = df.at[i, "balance"]
        if prev_balance == 0 and curr_balance == 0:
            continue
        expected = prev_balance + df.at[i, "credit"] - df.at[i, "debit"]
        if abs(expected - curr_balance) > 2:
            reasons[i].append("Running balance mismatch after transaction")
            rule_points[i] += 40
            strong_hits[i] = True

    df["rule_points"] = np.clip(rule_points, 0, 100).round(2)
    df["risk_score"] = np.clip((df["ml_score"] * 0.85) + (df["rule_points"] * 0.15), 0, 100).round(2)
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 25, 55, 100],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df["reason"] = ["; ".join(r) if r else "No strong anomaly signals" for r in reasons]
    multi_reason_hits = np.array([len(r) >= 2 for r in reasons], dtype=bool)

    df["fraud_flag"] = np.where(
        strong_hits | (df["risk_score"] >= 45) | ((df["risk_score"] >= 35) & multi_reason_hits),
        "Flagged",
        "Normal",
    )

    summary = {
        "total_txn": int(len(df)),
        "flagged_txn": int((df["fraud_flag"] == "Flagged").sum()),
        "total_debit": float(df["debit"].sum()),
        "total_credit": float(df["credit"].sum()),
        "avg_risk": float(df["risk_score"].mean()),
    }

    return df, summary
