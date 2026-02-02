import sys
import os
from unittest.mock import MagicMock

# Mock streamlit before importing data_fetch
sys.modules["streamlit"] = MagicMock()
sys.path.append(os.getcwd())

import data_fetch
import yfinance as yf
import concurrent.futures

# Reconstruct TICKER_MAP (mirroring search.py logic)
TICKER_MAP = {
    "NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "NIFTY": "^NSEI", "BANK NIFTY": "^NSEBANK"
}
for t in data_fetch.BLUECHIP_TICKERS:
    TICKER_MAP[t] = f"{t}.NS"
    TICKER_MAP[t.replace(".NS", "")] = f"{t}.NS"
for name, symbol in data_fetch.ETF_INDEX_SYMBOLS.items():
    TICKER_MAP[name.upper()] = symbol
    TICKER_MAP[name] = symbol
for sector, subcats in data_fetch.MARKET_DATA.items():
    for subcat_name, tickers in subcats.items():
        for t in tickers:
            clean_t = t.replace(".NS", "")
            TICKER_MAP[clean_t] = f"{clean_t}.NS"

def check_one(ticker_input):
    # Logic from search.py's robust fetcher
    initial_ticker = TICKER_MAP.get(ticker_input.upper(), ticker_input)
    base_ticker = initial_ticker.replace(".NS", "").replace(".BO", "")
    
    attempts = []
    if base_ticker.startswith("^"):
        attempts = [initial_ticker]
    else:
        attempts.append(f"{base_ticker}.NS")
        attempts.append(f"{base_ticker}.BO")
        # Add simpler base if not already present
        if base_ticker not in [f"{base_ticker}.NS", f"{base_ticker}.BO"]:
            attempts.append(base_ticker)
        if initial_ticker not in attempts:
            attempts.append(initial_ticker)

    # Dedup
    unique_attempts = []
    [unique_attempts.append(x) for x in attempts if x not in unique_attempts]

    for attempt in unique_attempts:
        try:
            # Use 5d to be quick but reliable
            hist = yf.Ticker(attempt).history(period="5d")
            if not hist.empty:
                return (True, ticker_input, attempt)
        except:
            pass
    return (False, ticker_input, unique_attempts)

print(f"Checking {len(TICKER_MAP)} items with {len(TICKER_MAP.keys())} unique keys...")
failures = []
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    futures = {executor.submit(check_one, k): k for k in TICKER_MAP.keys()}
    for future in concurrent.futures.as_completed(futures):
        success, name, meta = future.result()
        if not success:
            print(f"XX FAILED: {name} (Tried: {meta})")
            failures.append(name)
        else:
            pass # Success

with open("failures.txt", "w") as f:
    f.write(f"Total Failures: {len(failures)}\n")
    for fail in failures:
        f.write(f"{fail}\n")
print("Results written to failures.txt")
