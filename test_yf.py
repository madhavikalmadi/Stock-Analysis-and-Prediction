import yfinance as yf
print(f"yfinance version: {yf.__version__}")
stk = yf.Ticker("MSFT")
print(f"Ticker: {stk.ticker}")
