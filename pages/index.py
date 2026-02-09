import streamlit as st
import numpy as np
import pandas as pd
import os, sys

import data_fetch
import metric_calculator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import auth_utils


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Index Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# 🔁 RESTORE SESSION FROM URL (VERY IMPORTANT)
# =====================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# =====================================================
# 🔄 PERSIST SESSION (VERY IMPORTANT)
# =====================================================
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ❌ NO LOGIN REDIRECT HERE
# Dashboard already guarantees authentication

# =====================================================
# STYLES
# =====================================================
st.markdown("""
<style>
.stock-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border-top: 5px solid #22c55e;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.big { font-size: 2rem; font-weight: 800; color:#16a34a; }
.small { color:#64748b; font-size:0.8rem; }
.metric { font-weight:700; }

div.stButton > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.85rem !important;
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.85) !important;
    color: white !important;
    white-space: nowrap !important;
}
div.stButton > button:hover {
    background: #2563eb !important;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# TITLE
# =====================================================
st.title("🏆 Market Leaderboard")
st.write("### 10-Year Risk-Adjusted Index Performance (Academic Analysis)")


# =====================================================
# DROPDOWN
# =====================================================
choice = st.selectbox(
    "Select Index",
    ["Select..."] + list(data_fetch.ETF_INDEX_SYMBOLS.keys())
)

selected_indices = list(data_fetch.ETF_INDEX_SYMBOLS.keys())


# =====================================================
# HELPERS
# =====================================================
def normalize(series: pd.Series) -> pd.Series:
    series = series.clip(
        lower=series.quantile(0.05),
        upper=series.quantile(0.95)
    )
    return (series - series.min()) / (series.max() - series.min())


# =====================================================
# ANALYZE
# =====================================================
if st.button("🚀 Analyze Market Indices"):

    with st.spinner("Calculating 10-year risk-adjusted performance..."):

        tickers = [
            data_fetch.ETF_INDEX_SYMBOLS[name]
            for name in selected_indices
        ]

        price_data = data_fetch.fetch_stock_data(tickers, period="10y")

        if price_data.empty:
            st.error("Unable to fetch data.")
            st.stop()

        metrics = metric_calculator.compute_metrics(
            price_data,
            market_ticker="^NSEI",
            risk_free_rate=0.06
        )

        ranked = metrics.copy()

        ranked["CAGR_S"]   = normalize(ranked["CAGR"])
        ranked["Sharpe_S"] = normalize(ranked["Sharpe"])
        ranked["Vol_S"]    = 1 - normalize(ranked["Volatility"])
        ranked["DD_S"]     = 1 - normalize(abs(ranked["MaxDrawdown"]))

        ranked["Score"] = (
            0.35 * ranked["CAGR_S"] +
            0.25 * ranked["Sharpe_S"] +
            0.20 * ranked["Vol_S"] +
            0.20 * ranked["DD_S"]
        ) * 100

        ranked = ranked.sort_values("Score", ascending=False).reset_index(drop=True)

        name_map = {v: k for k, v in data_fetch.ETF_INDEX_SYMBOLS.items()}
        ranked["Name"] = ranked["Ticker"].map(name_map)

    # =====================================================
    # RESULT CARDS
    # =====================================================
    cols = st.columns(len(ranked))

    for i, row in ranked.iterrows():
        with cols[i]:
            label = "🥇 Winner" if i == 0 else f"#{i+1}"

            st.markdown(f"""
<div class="stock-card">
<div class="metric" style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:2px;">{row['Name']}</div>
<div class="small" style="font-size:0.85rem; color:#64748b; margin-bottom:10px; min-height:30px; display:flex; align-items:center; justify-content:center; line-height:1.2;">{label}</div>
<div class="small" style="font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; color:#64748b; margin-bottom:2px;">Risk-Adjusted Score</div>
<div class="big" style="margin-bottom:15px; color:#059669;">{row['Score']:.1f}<span style="font-size:1rem; color:#94a3b8;">/100</span></div>
<div class="metrics-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; padding-top:15px; border-top:1px solid #eee;">
<div><span class="small" style="font-weight:700;">CAGR</span><div style="font-weight:600;">{row['CAGR']*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Sharpe</span><div style="font-weight:600;">{row['Sharpe']:.2f}</div></div>
<div><span class="small" style="font-weight:700;">Vol</span><div style="font-weight:600;">{row['Volatility']*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Maximum DD</span><div style="font-weight:600; color:#ef4444;">{row['MaxDrawdown']*100:.1f}%</div></div>
</div>
</div>
""", unsafe_allow_html=True)

    # =====================================================
    # 📌 REASON / GUIDANCE MESSAGE
    # =====================================================
    st.markdown("---")

    top_row = ranked.iloc[0]
    top_index = top_row["Name"]

    if choice != "Select...":
        selected_row = ranked[ranked["Name"] == choice].iloc[0]

        if choice == top_index:
            st.success(
                f"✅ **{top_index}** ranks highest based on 10-year "
                f"risk-adjusted performance, making it the most optimal "
                f"index for long-term academic comparison."
            )
        else:
            st.info(
                f"ℹ️ You selected **{choice}**, however **{top_index}** "
                f"outperforms it on key metrics.\n\n"
                f"**Reason to switch:**\n"
                f"- Higher CAGR ({top_row['CAGR']*100:.1f}% vs {selected_row['CAGR']*100:.1f}%)\n"
                f"- Better Sharpe Ratio ({top_row['Sharpe']:.2f} vs {selected_row['Sharpe']:.2f})\n"
                f"- Lower volatility and drawdowns\n\n"
                f"📌 *Hence, **{top_index}** offers a superior risk–return "
                f"trade-off over the last decade.*"
            )

    # =====================================================
    # 🧾 EXPLANATION OF TERMS (DROPDOWN)
    # =====================================================
    st.write("")
    st.markdown("### 📚 Explanation of Key Terms")
    with st.expander("Click to learn more about the metrics used above", expanded=False):
        st.markdown("""
        * **Risk-Adjusted Score:** Our "Best of the Best" score. It picks indices that make money consistently without crashing often.
        * **CAGR** (Yearly Growth): The average speed at which your wealth grows each year.
        * **Sharpe** (Efficiency): Returns divided by Risk. A high Sharpe ratio means you are getting "paid" well for the risk you take.
        * **Vol** (Volatility): Indices with lower volatility are smoother and easier to hold during bad times.
        * **Maximum DD** (Crash Safety): Measures how deep the index fell during the worst market crash. Lower drops mean your capital is safer.
        """)


# =====================================================
# 🔻 BOTTOM NAVIGATION (VISIBLE FROM START)
# =====================================================
st.write("")
st.markdown("---")
st.write("")

c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back to Menu", key="btn_index_back"):
        st.switch_page("pages/reinvestor.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_index_dashboard"):
        # Preserve session state in query params
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/dashboard.py")