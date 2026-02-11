import pandas as pd
import numpy as np
import streamlit as st

# --------------------------------------------------------------
# Weight Configurations
# --------------------------------------------------------------

weight_models = {
    "EqualWeight": {
        "CAGR": 0.125,
        "Sharpe": 0.125,
        "Sortino": 0.125,
        "Calmar": 0.125,
        "Volatility": 0.125,
        "MaxDrawdown": 0.125,
        "Beta": 0.125,
        "RecoveryDays": 0.125
    },

    "BalancedModel": {
        "CAGR": 0.2,
        "Sharpe": 0.15,
        "Sortino": 0.15,
        "Calmar": 0.15,
        "Volatility": 0.1,
        "MaxDrawdown": 0.1,
        "Beta": 0.1,
        "RecoveryDays": 0.05
    },

    "RiskPriority": {
        "CAGR": 0.1,
        "Sharpe": 0.15,
        "Sortino": 0.2,
        "Calmar": 0.1,
        "Volatility": 0.15,
        "MaxDrawdown": 0.15,
        "Beta": 0.1,
        "RecoveryDays": 0.05
    }
}

# --------------------------------------------------------------
# Core Ranking Engine (Flexible Weights)
# --------------------------------------------------------------

@st.cache_data
def rank_with_weights(metrics_df, weight_dict):
    if metrics_df.empty:
        return metrics_df

    calc_df = metrics_df.copy()

    # Handle RecoveryDays penalty
    if "RecoveryDays" in calc_df.columns:
        max_recovery = calc_df["RecoveryDays"].max()
        if pd.isna(max_recovery):
            max_recovery = 2520  # fallback
        penalty_value = max_recovery * 1.5
        calc_df["RecoveryDays"] = calc_df["RecoveryDays"].fillna(penalty_value)

    calc_df = calc_df.select_dtypes(include=[np.number]).fillna(0)

    invert_columns = ["Volatility", "MaxDrawdown", "RecoveryDays"]

    for col in calc_df.columns:
        if col in weight_dict:
            # Inversion for risk metrics
            if col in invert_columns:
                calc_df[col] = 1 / (calc_df[col].abs() + 1e-6)

            # Min-Max Normalization
            min_val = calc_df[col].min()
            max_val = calc_df[col].max()

            if max_val - min_val != 0:
                calc_df[col] = (calc_df[col] - min_val) / (max_val - min_val)
            else:
                calc_df[col] = 0.0

    weight_series = pd.Series(weight_dict)
    common_cols = calc_df.columns.intersection(weight_series.index)

    final_scores = calc_df[common_cols].dot(weight_series[common_cols])

    result_df = metrics_df.copy()
    result_df["FinalScore"] = final_scores

    result_df = result_df.sort_values("FinalScore", ascending=False).reset_index(drop=True)

    return result_df

# --------------------------------------------------------------
# Default Ranking (Balanced Model)
# --------------------------------------------------------------

def rank_stocks(metrics_df):
    return rank_with_weights(metrics_df, weight_models["BalancedModel"])

# --------------------------------------------------------------
# Sensitivity Analysis
# --------------------------------------------------------------

def run_sensitivity_analysis(metrics_df):
    if metrics_df.empty:
        return {}

    ranking_results = {}
    top_rankings = {}

    for model_name, weights in weight_models.items():
        ranked_df = rank_with_weights(metrics_df, weights)

        # IMPORTANT: assuming 'Ticker' column exists
        if "Ticker" in ranked_df.columns:
            top_rankings[model_name] = ranked_df.head(5)["Ticker"].tolist()
        else:
            # fallback if ticker not available
            top_rankings[model_name] = ranked_df.head(5).index.tolist()

    base_set = set(top_rankings["BalancedModel"])

    for model_name, top_list in top_rankings.items():
        overlap = len(base_set.intersection(set(top_list)))

        ranking_results[model_name] = {
            "Top5Overlap": overlap,
            "OverlapPercentage": round((overlap / 5) * 100, 2),
            "Top5List": top_list
        }

    return ranking_results
