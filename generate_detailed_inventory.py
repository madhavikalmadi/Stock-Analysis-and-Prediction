import sys
import os
import yfinance as yf
import pandas as pd
from unittest.mock import MagicMock
import time

# Mock streamlit to avoid runtime errors when importing data_fetch
sys.modules["streamlit"] = MagicMock()

# Add current directory to path
sys.path.append(os.getcwd())

import data_fetch

def get_company_name(ticker_symbol):
    try:
        # Handle suffixes
        if not ticker_symbol.endswith(".NS") and not ticker_symbol.endswith(".BO") and not ticker_symbol.startswith("^"):
            ticker_symbol += ".NS"
            
        ticker = yf.Ticker(ticker_symbol)
        # Try to get shortName or longName
        info = ticker.info
        return info.get('longName') or info.get('shortName') or ticker_symbol
    except Exception as e:
        return ticker_symbol

def generate_detailed_report():
    print("Starting detailed stock inventory generation...")
    market_data = data_fetch.MARKET_DATA
    bluechip_tickers = data_fetch.BLUECHIP_TICKERS
    
    report_lines = []
    report_lines.append("# 📊 Comprehensive Stock Inventory with Company Names")
    report_lines.append("")
    report_lines.append("> **Note:** Company names fetched via Yahoo Finance. Some may default to ticker if fetch failed.")
    report_lines.append("")
    
    # Process Bluechip Tickers
    print(f"Processing {len(bluechip_tickers)} Bluechip tokens...")
    report_lines.append("## 🏆 NIFTY 50 Bluechips (Core List)")
    
    # Use a cache to avoid re-fetching the same ticker multiple times in the run
    name_cache = {}

    def fetch_name_cached(t):
        if t in name_cache:
            return name_cache[t]
        name = get_company_name(t)
        name_cache[t] = name
        # Rate limit slightly
        time.sleep(0.1) 
        return name

    # Table header
    report_lines.append("| Ticker | Company Name |")
    report_lines.append("|---|---|")
    
    for t in sorted(bluechip_tickers):
        name = fetch_name_cached(t)
        report_lines.append(f"| `{t}` | {name} |")
        print(f"Fetched: {t} -> {name}")
        
    report_lines.append("")

    # Process Market Data Divisions
    print("Processing Market Data Divisions...")
    for division, sectors in market_data.items():
        report_lines.append(f"## {division}")
        
        for sector_name, tickers in sectors.items():
            report_lines.append(f"### {sector_name}")
            report_lines.append("| Ticker | Company Name |")
            report_lines.append("|---|---|")
            
            for t in tickers:
                clean_t = t.replace('.NS', '').replace('.BO', '')
                name = fetch_name_cached(clean_t)
                report_lines.append(f"| `{clean_t}` | {name} |")
                
            report_lines.append("")
            
    output_path = r"C:\Users\Madhavi K\.gemini\antigravity\brain\bfcc764c-f70f-4b8b-b21a-29f136b89178\complete_stock_details.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Detailed report generated at: {output_path}")

if __name__ == "__main__":
    generate_detailed_report()
