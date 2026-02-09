
import yfinance as yf
import pandas as pd

try:
    print("Attempting to download TCS.NS...")
    data = yf.download(["TCS.NS"], period="5d", progress=False, auto_adjust=True)
    print("\nShape:", data.shape)
    print("Columns:", data.columns)
    print("Head:\n", data.head())
    
    if data.empty:
        print("Data is empty!")
    
    print("\nAttempting to download TCS.NS and INFY.NS...")
    data2 = yf.download(["TCS.NS", "INFY.NS"], period="5d", progress=False, auto_adjust=True)
    print("\nShape:", data2.shape)
    print("Columns:", data2.columns)
    print("Head:\n", data2.head())

except Exception as e:
    print(f"Error: {e}")
