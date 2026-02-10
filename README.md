# 📈 Smart Investor Assistant

A comprehensive, performance-driven stock analysis platform built with **Streamlit**. This tool helps users analyze the Indian Stock Market (NSE/BSE) using academic-grade metrics and real-time data.

## 🚀 Key Features

- **Personalized Dashboard**: Real-time market state monitoring (IST timezone) and a personal "Analysis Feed" showing your saved watchlist.
- **Sector & Thematic Advisor**: Compare entire market categories (Banking, IT, Auto, etc.) to find top-performing stocks.
- **Market Leaderboard**: 10-year risk-adjusted scoring to identify long-term market winners.
- **Knowledge Hub**: In-depth stock exploration with interactive performance charts and profile summaries.
- **Company Advisor**: Dual-mode analysis supporting single stock deep-dives and head-to-head comparisons.
- **Universal Search**: Intelligent shortcut-based search (e.g., "infy" for Infosys) and full ticker support.

## 🛠 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python-based interactive UI)
- **Data (Market)**: [yfinance](https://github.com/ranaroussi/yfinance) (Yahoo Finance API)
- **Data (Persistence)**: [MongoDB](https://www.mongodb.com/) (User profiles & watchlist storage)
- **Analytics Engine**: Custom Python metrics (`CAGR`, `Sharpe Ratio`, `Sortino`, `Max Drawdown`, `Recovery Days`)
- **Backend**: Python 3.9+ with Pandas and NumPy for vectorized financial computing.

## 📊 Data Architecture

### 1. Market Data (Yahoo Finance)
The platform fetches real-time and historical OHLC (Open, High, Low, Close) data. While it downloads the full OHLC structure, it primarily uses **Adjusted Close Prices** for performance calculations to ensure consistency across corporate actions like splits and dividends.

### 2. User Data (MongoDB)
- **Authentication**: Secure login/signup system with role-based access (Admin/Regular).
- **Persistence**: User watchlists and profile meta-data are stored in cloud collections, ensuring your analysis is available on any device.

## ⚙️ Setup & Installation

Follow these steps to run the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/madhavikalmadi/Stock-Analysis-and-Prediction.git
   cd Stock-Analysis-and-Prediction
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file or add to `st.secrets`:
   - `MONGO_URI`: Your MongoDB connection string.

4. **Run the Application**:
   ```bash
   streamlit run login.py
   ```

## 🔐 Credentials
- **Admin Access**: Specific features are reserved for admin users.
- **Benchmark**: The platform uses `NIFTYBEES.NS` as the default market benchmark for most risk-return calculations.

---
*Built for smarter, data-driven investing.*
