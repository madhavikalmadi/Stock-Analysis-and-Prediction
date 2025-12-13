Smart Investor – Stock Analysis & Prediction Dashboard
A complete investment assistant built with Streamlit, yfinance, and advanced financial scoring.

🚀 Overview
Smart Investor is a multi-module Streamlit application designed for beginners and reinvestors who want to analyze, compare, and validate stock investment decisions.

This project includes:
- Company Analyzer (CAGR, Sharpe, Sortino, Volatility, Beta, Max Drawdown, Recovery Days)
- Index Analyzer (Nifty ETFs ranking with 10-year backtest)
- Bluechip Explorer (Renders top 10 stocks based on Decision Score)
- Knowledge Hub (Beginner & Pro learning modules with animations, examples, and quizzes)
- Live Market Data using yfinance
- Interactive UI with animations, cards, scoring bars, and recommendations

Why This Project?
Traditional stock apps only show charts.
This app actually tells the user WHAT to choose and WHY.
Using 8 advanced financial metrics, the scoring engine ranks stocks for long-term investing:
- CAGR
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Volatility
- Max Drawdown
- Beta
- Recovery Days
These combine into a Decision Score (0–100) used throughout the system.
      
Installation & Setup
- Clone the Project
git clone https://github.com/madhavikalmadi/Stock-Analysis-and-Prediction.git
cd Stock-Analysis-and-Prediction
- Install Required Packages
pip install -r requirements.txt
If requirements.txt is missing, generate it:
pip freeze > requirements.txt
- Run the App
streamlit run app.py

Requirements
- streamlit
- yfinance
- numpy
- pandas
- requests
- plotly
- altair
- streamlit-lottie

Financial Metrics Used
| Metric         | Purpose                          |
| -------------- | -------------------------------- |
| CAGR           | Long-term growth measurement     |
| Sharpe Ratio   | Return per unit of total risk    |
| Sortino Ratio  | Return per unit of downside risk |
| Calmar Ratio   | Stability vs deep losses         |
| Volatility     | Price fluctuation risk           |
| Max Drawdown   | Largest historical drop          |
| Beta           | Relation to market risk          |
| Recovery Days  | Time to recover after crash      |
| Decision Score | Weighted ranking algorithm       |

How Recommendation Works
Each stock gets a Recommendation Tag:
✅ Strong Buy — High CAGR, good Sharpe, moderate volatility
⚠️ Moderate — Good potential but higher risk
❌ Avoid — Weak fundamentals, unstable performance

Roadmap / Future Features
- Add machine learning LSTM predictions
- Add sector-wise ETFs & analysis
- Add sentiment analysis using Twitter API
- Deploy on Streamlit Cloud / Vercel
- Add Portfolio Builder & Risk Profiler


