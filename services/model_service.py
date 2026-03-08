import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


MODEL_PATH = os.path.join("models", "fraud_model.pkl")


def score_anomalies(features_df: pd.DataFrame):
    if features_df.empty:
        return pd.Series(dtype=float), pd.Series(dtype=int)

    if len(features_df) < 5:
        amount = pd.to_numeric(features_df["amount"], errors="coerce").fillna(0.0)
        std = amount.std()
        if std == 0:
            score = pd.Series(0.0, index=features_df.index)
        else:
            score = ((amount - amount.mean()).abs() / std).clip(0, 3) / 3
        pred = score.apply(lambda x: -1 if x > 0.67 else 1)
        return score, pred

    model = IsolationForest(
        n_estimators=200,
        contamination=0.10,
        random_state=42,
    )
    model.fit(features_df)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    raw_score = pd.Series(-model.decision_function(features_df), index=features_df.index)
    if raw_score.max() == raw_score.min():
        norm_score = pd.Series(0.0, index=features_df.index)
    else:
        norm_score = (raw_score - raw_score.min()) / (raw_score.max() - raw_score.min())

    pred = pd.Series(model.predict(features_df), index=features_df.index)
    return norm_score, pred
