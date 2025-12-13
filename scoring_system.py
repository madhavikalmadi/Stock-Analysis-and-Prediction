import pandas as pd
import numpy as np
import streamlit as st

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
# Normalize and Score (Cached & Vectorized)
# --------------------------------------------------------------
@st.cache_data
def rank_stocks(metrics_df):
    if metrics_df.empty:
        return metrics_df

    # 1. Create a copy strictly for calculation so we don't mess up display values
    #    (Users want to see '15% CAGR', not '0.8 Normalized Score')
    calc_df = metrics_df.copy()

    # Fill NaNs to avoid crashes during calculation
    calc_df = calc_df.select_dtypes(include=[np.number]).fillna(0)

    # 2. Normalize metrics 
    # (higher = better, except for Volatility/Drawdown/Recovery which are inverted)
    invert_columns = ["Volatility", "MaxDrawdown", "RecoveryDays"]
    
    for col in calc_df.columns:
        if col in weights: # Only process columns we have weights for
            # Handle Inversion: 
            # We use 1/(x) logic from your original code, but protected against zero
            if col in invert_columns:
                calc_df[col] = 1 / (calc_df[col].abs() + 1e-6)
            
            # Min-Max Normalization (Scale to 0-1 range)
            min_val = calc_df[col].min()
            max_val = calc_df[col].max()
            
            if max_val - min_val != 0:
                calc_df[col] = (calc_df[col] - min_val) / (max_val - min_val)
            else:
                calc_df[col] = 0.0 # If all values are same, score is 0

    # 3. Vectorized Scoring (Much faster than looping)
    # Align weights with the dataframe columns
    weight_series = pd.Series(weights)
    
    # Filter calc_df to only include columns present in weights
    common_cols = calc_df.columns.intersection(weight_series.index)
    
    # Calculate Dot Product (The Weighted Sum)
    final_scores = calc_df[common_cols].dot(weight_series[common_cols])

    # 4. Return ORIGINAL data with the new Score attached
    result_df = metrics_df.copy()
    result_df["FinalScore"] = final_scores
    
    # Sort by FinalScore
    result_df = result_df.sort_values("FinalScore", ascending=False).reset_index(drop=True)
    
    return result_df