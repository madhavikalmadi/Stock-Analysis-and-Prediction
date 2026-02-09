
import data_fetch
import pandas as pd
import yfinance as yf
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_tickers(category_name, tickers):
    print(f"\n🚀 Checking {category_name} ({len(tickers)} tickers)...")
    failed = []
    
    # Process in batches of 10 to speed up but stay within limits
    batch_size = 10
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"  Batch {i//batch_size + 1}: {batch}")
        
        try:
            # We use fetch_stock_data from data_fetch which handles yf.download
            # Using a short period to be fast
            data = data_fetch.fetch_stock_data(batch, period="5d")
            
            if data.empty:
                print(f"  ⚠️  WARNING: No data returned for batch {batch}")
                failed.extend(batch)
                continue
                
            # Check which columns are missing (if multi-index)
            # data_fetch.fetch_stock_data returns a DataFrame where columns are the Tickers (Close prices)
            # So we just need to check the columns
            returned_tickers = [c.replace(".NS", "") for c in data.columns]
            
            # The input batch might have .NS or not, let's normalize both to compare
            batch_normalized = [t.replace(".NS", "") for t in batch]
            returned_normalized = set(returned_tickers)
            
            missing = set(batch_normalized) - returned_normalized
            if missing:
                print(f"  ❌ Missing data for: {missing}")
                failed.extend(list(missing))
                
        except Exception as e:
            print(f"  ❌ Error fetching batch: {e}")
            failed.extend(batch)
            
    return failed

all_failures = {}

# 1. BLUECHIP
print("--- 1. BLUECHIP TICKERS ---")
failed_bluechip = check_tickers("Bluechip", data_fetch.BLUECHIP_TICKERS)
if failed_bluechip: all_failures["Bluechip"] = failed_bluechip

# 2. INDICES (index.py)
print("\n--- 2. INDICES ---")
indices_tickers = list(data_fetch.ETF_INDEX_SYMBOLS.values())
failed_indices = check_tickers("Indices", indices_tickers)
if failed_indices: all_failures["Indices"] = failed_indices

# 3. SECTOR (sector.py)
print("\n--- 3. SECTOR TICKERS ---")
sector_tickers = []
for cat, subcats in data_fetch.MARKET_DATA.items():
    for subcat, tickers in subcats.items():
        sector_tickers.extend(tickers)
# Remove duplicates
sector_tickers = list(set(sector_tickers))
failed_sector = check_tickers("Sector", sector_tickers)
if failed_sector: all_failures["Sector"] = failed_sector

# 4. SEARCH (search.py)
# Note: SEARCH_SHORTCUTS maps name -> ticker. We need the values.
print("\n--- 4. SEARCH SHORTCUTS ---")
search_tickers = list(data_fetch.SEARCH_SHORTCUTS.values())
# Also check STOCK_COMPANY_MAP keys (implied tickers mostly, but let's check explicit map first)
failed_search = check_tickers("Search Shortcuts", search_tickers)
if failed_search: all_failures["Search"] = failed_search

print("\n\n===========================================")
print("FINAL VARIFICATION REPORT")
print("===========================================")
if not all_failures:
    print("✅✅ ALL SYSTEMS GO! All tickers are valid and fetching data.")
else:
    print("❌ FOUND BROKEN TICKERS:")
    for cat, tickers in all_failures.items():
        print(f"\nCategories: {cat}")
        for t in tickers:
            print(f" - {t}")
