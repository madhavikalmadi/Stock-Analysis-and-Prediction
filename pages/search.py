import streamlit as st
import yfinance as yf
import pandas as pd
from db import execute

st.set_page_config(page_title="Stock Search", page_icon="🔍", layout="wide")

# SESSION STATE
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# TICKER MAP
TICKER_MAP = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "INFOSYS": "INFY",
    "HDFC BANK": "HDFCBANK",
}

@st.cache_data(ttl=300)
def fetch_stock_data(ticker_input):
    ticker = TICKER_MAP.get(ticker_input.upper(), ticker_input)
    stock = yf.Ticker(ticker)
    history = stock.history(period="2d")

    if history.empty:
        return None, "Not found"

    price = history["Close"].iloc[-1]
    prev = history["Close"].iloc[-2]
    change = ((price - prev) / prev) * 100

    return {
        "ticker": ticker,
        "price": price,
        "change": change
    }, None

def add_to_watchlist(ticker):
    if ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(ticker)

        execute(
            "INSERT INTO user_actions (user_id, action, value) VALUES (:u, 'save', :v)",
            {"u": st.session_state.get("user_id"), "v": ticker},
        )

        st.toast(f"⭐ Saved {ticker}")

# UI
st.title("🔍 Stock Search")

search_input = st.text_input(
    "Enter Stock Ticker",
    value=st.session_state.search_query
)

# Only log if search changed
if search_input and search_input != st.session_state.search_query:
    st.session_state.search_query = search_input

    execute(
        "INSERT INTO user_actions (user_id, action, value) VALUES (:u, 'search', :v)",
        {"u": st.session_state.get("user_id"), "v": search_input},
    )

    stock_data, error = fetch_stock_data(search_input)

    if stock_data:
        st.metric("Price", f"₹ {stock_data['price']:.2f}", f"{stock_data['change']:+.2f}%")
        st.button("⭐ Save", on_click=add_to_watchlist, args=(stock_data["ticker"],))
    else:
        st.error(error)
