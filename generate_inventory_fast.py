import sys
import os
import yfinance as yf
import pandas as pd
from unittest.mock import MagicMock
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Mock streamlit
sys.modules["streamlit"] = MagicMock()
sys.path.append(os.getcwd())
import data_fetch

def get_company_name_safe(ticker_symbol):
    try:
        clean_symbol = ticker_symbol.replace('.NS', '').replace('.BO', '')
        # Add .NS for Indian stocks if not present and not an index
        query_symbol = ticker_symbol
        if not query_symbol.endswith(".NS") and not query_symbol.endswith(".BO") and not query_symbol.startswith("^"):
            query_symbol += ".NS"
            
        ticker = yf.Ticker(query_symbol)
        # Use fast info access if possible
        info = ticker.info
        name = info.get('longName') or info.get('shortName') or clean_symbol
        return ticker_symbol, name
    except:
        return ticker_symbol, ticker_symbol

def generate_detailed_report():
    print("Starting optimized stock inventory generation...")
    market_data = data_fetch.MARKET_DATA
    bluechip_tickers = data_fetch.BLUECHIP_TICKERS
    
    # Collect all unique tickers first to batch process
    all_tickers = set(bluechip_tickers)
    for div in market_data.values():
        for tickers in div.values():
            all_tickers.update(tickers)
            
    all_tickers = list(all_tickers)
    print(f"Fetching names for {len(all_tickers)} unique stocks...")
    
    name_map = {}
    
    # Parallel Fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(get_company_name_safe, t): t for t in all_tickers}
        for future in as_completed(future_to_ticker):
            t = future_to_ticker[future]
            try:
                orig_t, name = future.result()
                name_map[orig_t] = name
                # print(f"Fetched: {orig_t} -> {name}") # Reduce spam for speed
            except Exception as exc:
                name_map[t] = t
                
    print("Fetch complete. Generating report...")
    
    report_lines = []
    report_lines.append("# 📊 Comprehensive Stock Inventory with Company Names")
    report_lines.append("")
    report_lines.append(f"**Total Stocks:** {len(all_tickers)}")
    report_lines.append("")
    
    # Bluechips
    report_lines.append("## 🏆 NIFTY 50 Bluechips (Core List)")
    report_lines.append("| Ticker | Company Name |")
    report_lines.append("|---|---|")
    for t in sorted(bluechip_tickers):
        report_lines.append(f"| `{t}` | {name_map.get(t, t)} |")
    report_lines.append("")
    
    # Market Data
    for division, sectors in market_data.items():
        report_lines.append(f"## {division}")
        for sector_name, tickers in sectors.items():
            report_lines.append(f"### {sector_name}")
            report_lines.append(f"**Count:** {len(tickers)}")
            report_lines.append("| Ticker | Company Name |")
            report_lines.append("|---|---|")
            for t in sorted(tickers):
                report_lines.append(f"| `{t}` | {name_map.get(t, t)} |")
            report_lines.append("")
            
    output_path = r"C:\Users\Madhavi K\.gemini\antigravity\brain\bfcc764c-f70f-4b8b-b21a-29f136b89178\complete_stock_details.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Detailed report generated at: {output_path}")

if __name__ == "__main__":
    generate_detailed_report()
