import pandas as pd
import numpy as np

# --------------------------------------------------------------
# Define Weights for User Type
# --------------------------------------------------------------
weights = {
    "CAGR": 0.2,
    "Sharpe": 0.15,
    "Sortino": 0.15,
    "Calmar": 0.15,
    "Volatility": 0.1,
    "MaxDrawdown": 0.1,
    "Beta": 0.1,
    "RecoveryDays": 0.05
}

# --------------------------------------------------------------
# Normalize and Score
# --------------------------------------------------------------
def rank_stocks(metrics_df):
    df = metrics_df.copy()

    # Normalize metrics (higher = better except volatility, drawdown, recovery days)
    invert = ["Volatility", "MaxDrawdown", "RecoveryDays"]
    for col in df.columns:
        if col not in ["Ticker"]:
            if col in invert:
                df[col] = 1 / (df[col].abs() + 1e-6)
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # Weighted score
    df["FinalScore"] = sum(df[k] * v for k, v in weights.items())
    df = df.sort_values("FinalScore", ascending=False).reset_index(drop=True)
    return df