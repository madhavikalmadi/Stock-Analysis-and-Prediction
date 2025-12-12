import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import requests
from streamlit_lottie import st_lottie
import os

# ==============================================================================
# 1. CONFIGURATION & ASSET LOADING
# ==============================================================================
st.set_page_config(
    page_title="Knowledge Hub | Smart Investor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_lottieurl(url: str):
    """Helper to load lottie animations from URL."""
    try:
        r = requests.get(url, timeout=3)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def load_assets():
    """Loads all necessary assets (animations) at once."""
    return {
        "plant": load_lottieurl("https://lottie.host/9d31154c-7c0b-44ec-b50e-744046429940/3Y2Rj8w0yY.json"),
        "chart": load_lottieurl("https://lottie.host/f7c10f63-0975-4089-a2f0-1563f847343d/dK0yS0nZ5J.json"),
        "check": load_lottieurl("https://lottie.host/80e3636b-7334-4b47-9257-23425f05359c/Qk5r24rTj5.json"),
        "success": load_lottieurl("https://lottie.host/98014498-8422-4881-bb03-4d402b800645/6T39I2b9K1.json")
    }

# ==============================================================================
# 2. CONTENT RENDERERS
# ==============================================================================

def render_beginner_zone(lotties):
    # --- HEADER ---
    st.markdown("""
    <div class="glass-container" style="padding: 1.5rem; text-align: center;">
        <span style="font-size: 1.1rem;">
            🎯 <b>Goal:</b> Understand what a stock is, how the market works, and the core differences between trading and investing.
        </span>
    </div>""", unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    st.markdown("<div class='sub-header'>🐣 The Absolute Basics</div>", unsafe_allow_html=True)

    # 1. PIZZA ANALOGY
    with st.expander("❓ What is a Stock? (The Pizza Analogy)", expanded=False):
        tc, cc = st.columns([1.3, 1])
        with tc:
            st.markdown("""
            Imagine a company is a **Giant Pizza** 🍕. The founders want to expand, but they can't afford the ingredients (capital) alone. So, they slice the pizza into millions of tiny pieces. When you buy a "Stock," you are buying **one slice** of that pizza.
            
            **Why does the price change?**
            If the pizza shop starts using better cheese and selling more pizzas (higher profits), everyone wants a slice, so the price goes **UP**. If they burn the pizza (losses), nobody wants it, and the price goes **DOWN**.
            """)
        with cc:
            try:
                st.image("images/pizza.png", use_container_width=True)
            except:
                st.error("Image not found at 'images/pizza.png'")

    # 2. SHARE MARKET
    with st.expander("🏛️ What is the Share Market? (The Supermarket)"):
        st.markdown("""
        It is simply a **Supermarket for Second-hand Shares** 🛒.
        
        * If you want to buy tomatoes, you go to a vegetable market.
        * If you want to buy Reliance shares, you go to the **Stock Market** (NSE or BSE).
        
        **Crucial Point:** You usually don't buy shares from the company itself. You buy them from *another person* (like John) who wants to sell them. The Market just introduces you to John.
        
        The **Bombay Stock Exchange (BSE)** is the oldest in Asia (established in 1875). Today, the Indian stock market trades thousands of crores of rupees **every single day**.
        """)
    
    # 3. SENSEX & NIFTY
    with st.expander("📉 What are Sensex and Nifty? (The Class Monitors)"):
        st.markdown("""
        Imagine a classroom with 5,000 students (companies). To know if the "class is happy," you can't ask every single student.
        
        Instead, you pick the **Top 50 smartest & richest students** (Nifty 50). If those 50 are doing well, you assume the whole economy is doing well.
        
        * **NIFTY 50:** Top 50 companies on NSE.
        * **SENSEX:** Top 30 companies on BSE.
        
        *History:* In 2002, Nifty was around 1,000 points. In 2024, it crossed 24,000 points. That represents the growth of the Indian economy.
        """)
        
    # 4. BULL VS BEAR
    with st.expander("🐂 Bull vs. Bear Market"):
        c1, c2 = st.columns(2)
        with c1:
            st.success("""
            **🐂 Bull Market (Optimism)**
            A Bull attacks by thrusting its horns **UP**. Describes a market that is rising, economy is growing, and people are greedy/happy.
            """)
        with c2:
            st.error("""
            **🐻 Bear Market (Pessimism)**
            A Bear attacks by swiping its paws **DOWN**. Describes a market that is falling, economy is slowing, and people are fearful.
            """)
        
        st.markdown("""
        A market is officially "Bear" if it drops **20% or more** from its high. For example, during the COVID-19 crash (March 2020), the market fell ~30% in a month (Bear). It then recovered and doubled (Bull).
        """)

    # 5. TRADING VS INVESTING (NEW ADDITION)
    with st.expander("🏏 Trading vs. Investing? (The Cricket Analogy)"):
        st.markdown("""
        **The Nice & Easy Explanation:**
        * **Trading (T20 Match):** Fast-paced. You buy and sell quickly (minutes, days, or weeks) to catch small price jumps. It is an active job, like hitting boundaries in a T20 match.
        * **Investing (Test Match):** The long game. You buy high-quality companies and hold them for years (or decades) to let your wealth compound. It is passive, like playing a steady Test match inning.
        """)

    # --- HOW IT WORKS ---
    st.markdown("<div class='sub-header'>⚙️ How It Works</div>", unsafe_allow_html=True)

    # 6. PRIMARY VS SECONDARY
    with st.expander("🔄 Primary vs. Secondary Market?"):
        st.markdown("""
        * **Primary Market (IPO):** Think of this as buying a **Brand New Car** from the showroom. You pay money, and the **Company** gets the cash.
        * **Secondary Market (Stock Exchange):** Think of this as buying a **Used Car** from your neighbor. You pay money, and your **Neighbor** gets the cash (the company gets nothing).
        
        When **Zomato** launched its IPO, it raised ₹9,375 Crores in the Primary Market. Now, millions of Zomato shares trade daily in the Secondary Market, but Zomato doesn't get that money; the traders do.
        """)

    # 7. MARKET HOURS
    with st.expander("🕒 Market Hours"):
        st.markdown("""
        The market isn't open 24/7 like Crypto. It works on banking hours.
        
        * **9:00 AM - 9:15 AM:** Pre-open (The engine warms up).
        * **9:15 AM:** **The Bell Rings.** Real trading starts. 🔔
        * **3:30 PM:** Market Closes.
        
        The Indian market is closed on Saturdays, Sundays, and public holidays. However, global events (like US election results) often happen when our market is closed, causing a "Gap Up" (opening higher) or "Gap Down" (opening lower) the next morning.
        """)

    # 8. MARKET CAP ZOO
    with st.expander("🐋 Large vs. Mid vs. Small Cap? (The Zoo)"):
        st.markdown("""
        🐘 Large Cap (Elephant): Massive companies (TCS, Reliance). They move slowly but are very strong. They act as a shield for your portfolio.
        - Large Cap: Valuation > ₹20,000 Crores.
        
        
        🐅 Mid Cap (Tiger): Growing companies (Polycab, Voltas). Faster than elephants, but can get hurt if the jungle (economy) gets bad.
        - Mid Cap: Valuation ₹5,000 - ₹20,000 Crores.

                    
        🐇 Small Cap (Rabbit): Tiny, new companies. They can run extremely fast (double your money), but they are fragile (can go to zero).
        - Small Cap: Valuation < ₹5,000 Crores.
        """)

    # --- MONEY MATTERS ---
    st.markdown("<div class='sub-header'>💰 Money Matters</div>", unsafe_allow_html=True)

    # 9. DIVIDENDS VS GROWTH
    with st.expander("💵 Dividends vs. Growth Stocks?"):
        st.markdown("""
        * **Dividend (The Cow):** You buy a cow. It gives you **Milk** (Cash/Dividends) regularly. You don't sell the cow; you just enjoy the passive income.
        * **Growth (The Calf):** You buy a baby calf. It gives **zero milk**. It eats all the food (profits) to grow bigger. You only make money when you sell the huge cow 5 years later.
        
        **Coal India** often has a Dividend Yield of 5-8%. This means if you invest ₹1 Lakh, they might pay you ₹5,000 - ₹8,000 cash per year just for holding the stock, regardless of the stock price!
        """)

    # 10. DEMAT ACCOUNT
    with st.expander("🏦 What is a Demat Account?"):
        st.markdown("""
        It is a **Digital Locker**.
        * You keep **Cash** in a *Savings Account*.
        * You keep **Shares** in a *Demat Account*.
        
        In the old days, people kept physical paper certificates under their mattresses. Now, shares are electronic files stored in your Demat account.
        """)

    # 11. TAXES
    with st.expander("💸 Taxes? (Giving Govt their share)"):
        st.markdown("""
        If you make money (profit), the government wants a slice of your pizza.
        
        * **Short Term (Impatient):** Sell before 1 year = **20% Tax**. (Govt penalizes you for treating market like a casino).
        * **Long Term (Patient):** Sell after 1 year = **12.5% Tax**. (Govt rewards you for investing for future).
        
        (As of July 2024 Budget): The first **₹1.25 Lakh** of Long Term profit you make in a year is **Tax-Free**. The government encourages small investors to save long-term!
        """)

    # --- QUIZ ---
    st.markdown("---")
    st.markdown("### 📝 Test Your Knowledge")
    with st.container():
        form = st.form("beginner_quiz")
        ans = form.radio("1. If you want 'Rent' (Cash) from a stock, what do you look for?", 
                         ["High P/E Ratio", "High Dividend Yield", "Stock Split"], index=None)
        if form.form_submit_button("Check My Answer"):
            if ans == "High Dividend Yield":
                st.success("🎉 Correct! Dividends are like rent payments.")
                if lotties["success"]: st_lottie(lotties["success"], height=150, key="succ_1")
            else:
                st.error("Try again! Hint: It's related to the 'Cow' analogy.")


def render_reinvestor_zone(lotties):
    # --- Header ---
    st.markdown("""
    <div class="glass-container" style="padding: 1.5rem; text-align: center;">
        <b>🎯 Goal:</b> Master valuation metrics (P/E, ROCE) and understand advanced portfolio strategies.
    </div>""", unsafe_allow_html=True)

    # --- Content ---
    st.markdown("<div class='sub-header'>📊 Valuation Strategies</div>", unsafe_allow_html=True)
    
    with st.expander("🏰 What is an Economic Moat?"):
        st.markdown("""
        Think of a company as a **Castle**. An "Economic Moat" is the deep water trench around the castle filled with alligators 🐊. It prevents enemies (competitors) from stealing your customers.
        
        *Examples of Moats:*
        * **Brand Power:** (Apple) People buy it even if it's expensive.
        * **Network Effect:** (WhatsApp) You use it because all your friends use it.
        
        ---
        **Warren Buffett** coined this term. Companies with wide moats (like **Google** in search) maintain high profit margins for decades because it's too hard for others to compete.
        """)

    with st.expander("🧪 What is ROCE? (The Efficiency Score)"):
        st.markdown("""
        **Return on Capital Employed (ROCE)** measures how smart the company's management is with your money.
        * If you give a manager ₹100, and they generate ₹20 profit, the ROCE is **20%**.
        * If another manager generates only ₹5, the ROCE is **5%**.
        * *You want the manager who generates ₹20!*
        
        ---
        In India, a "Superstar Company" typically has an ROCE of **above 20%** consistently for 5+ years (e.g., Asian Paints, TCS).
        """)

    with st.expander("⚖️ P/E vs. PEG Ratio"):
        st.markdown("""
        * **P/E (Price-to-Earnings):** Tells you if the stock is "Expensive". (Like looking at the price tag of a house).
        * **PEG (P/E to Growth):** Tells you if the "Expensive" price is **justified**. (Is the house in a booming neighborhood?).
        
        *Rule of Thumb:*
        * PEG < 1: Undervalued (Good Deal).
        * PEG > 1: Overvalued (Too Expensive).
        
        ---
        A stock with a high P/E (like 80) might look expensive, but if its profits are doubling every year, its PEG might be low (0.8), making it a great buy!
        """)

    st.markdown("<div class='sub-header'>🛡️ Portfolio Management</div>", unsafe_allow_html=True)
    
    with st.expander("📅 Dollar Cost Averaging / SIP"):
        st.markdown("""
        Instead of trying to guess the "Perfect Time" to buy (which is impossible), you buy a fixed amount every month (e.g., ₹5,000 on the 1st).
        * When market is **High**, you buy fewer units.
        * When market is **Low**, you buy more units.
        * *Result:* Your average cost stays low automatically!
        
        ---
        Historical data of Nifty 50 shows that SIPs (Systematic Investment Plans) over any 10-year period in India have **never** generated negative returns.
        """)

    with st.expander("🏹 Active vs. Passive Funds"):
        st.markdown("""
        * **Active Fund (Man vs Wild):** A fund manager (Human) tries to pick the best stocks to beat the market. They charge high fees.
        * **Passive Fund (Autopilot):** A computer simply copies the Index (Nifty 50). No thinking, just copying. Low fees.
        
        ---
        According to SPIVA reports, over a 10-year period, **~70-80% of Active Fund Managers FAIL** to beat the simple Passive Index due to human error and high fees.
        """)

    with st.expander("🧠 Market Psychology (FOMO & Panic)"):
        st.markdown("""
        Your biggest enemy in the stock market is not the economy, it is **YOU**.
        * **FOMO (Fear Of Missing Out):** Buying at the top because "everyone is making money." (Greed).
        * **Panic Selling:** Selling at the bottom because "the market is crashing." (Fear).
        * *Success comes from doing the opposite.*
        
        ---
        Studies show that investors who check their portfolio **daily** trade too much and earn significantly lower returns than those who check it **monthly**.
        """)

    st.markdown("<div class='sub-header'>❓ Common Reinvestor Doubts</div>", unsafe_allow_html=True)
    
    with st.expander("📉 What is Tax Loss Harvesting? (Lemonade from Lemons)"):
        st.markdown("""
        This is a smart trick to save tax.
        * Imagine you made **₹1 Lakh Profit** on Stock A (You owe tax).
        * But you have a **₹40,000 Loss** on Stock B.
        * You sell Stock B to "book the loss". Now your Net Profit is only **₹60,000**.
        * *Result:* You pay less tax! You can buy Stock B back later if you want.
        """)

    with st.expander("📊 CAGR vs. XIRR: Which to use?"):
        st.markdown("""
        * **CAGR:** Use this for **One-Time** investments (Lump sum). It's like measuring the average speed of a car from Point A to Point B.
        * **XIRR:** Use this for **SIPs** (Multiple investments). It accounts for the fact that every installment was invested for a different amount of time.
        """)

    with st.expander("⚠️ Is a High Dividend Yield always good? (The Trap)"):
        st.markdown("""
        **NO.** Be careful! Dividend Yield = (Dividend / Share Price).
        * If a share price **Crashes** from ₹100 to ₹50, the yield mathematically **Doubles**.
        * A very high yield (>10%) usually means the company is in trouble and the price has collapsed. It's a trap!
        
        ---
        Before **Vodafone Idea** stock crashed years ago, it had a high dividend yield. Investors who bought it just for the dividend lost massive capital when the share price fell further.
        """)

    with st.expander("🏗️ How many stocks should I own?"):
        st.markdown("""
        * **Too Few (< 5):** Too risky. If one fails, you lose everything.
        * **Too Many (> 30):** "Diworsification." You can't track them all, and your returns become average.
        * **The Sweet Spot:** **15 to 20** high-quality stocks gives you safety without diluting your profits.
        """)

    # --- Quiz ---
    st.markdown("---")
    st.markdown("### 📝 Pro Quiz: Test Your Strategy")
    form = st.form("pro_quiz")
    ans = form.radio("1. A PEG Ratio of < 1 usually indicates:", 
                     ["Overvalued", "Undervalued/Good", "No Growth"], index=None)
    if form.form_submit_button("Check Mastery"):
        if ans == "Undervalued/Good":
            st.success("🏆 Correct! You are a Pro.")
            if lotties["success"]: st_lottie(lotties["success"], height=150, key="succ_2")
        else:
            st.warning("Try again! (Hint: Growth justifies price)")

            st.stop()

# ==============================================================================
# 3. MAIN CONTROLLER
# ==============================================================================
def main():
    # 1. Load Styles
    load_css()
    
    # 2. Load Assets
    assets = load_assets()

    # 3. Render Hero
    with st.container():
        st.markdown("""
        <div class="hero-container">
            <div class='hero-title'>Knowledge Hub</div>
            <div class="hero-subtitle">Master the market concepts step-by-step</div>
            <div class="hero-desc">Clarify doubts, calculate returns, and verify your decisions before investing.</div>
        </div>
        """, unsafe_allow_html=True)
    st.write("")

    # 4. Initialize Session State
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "beginner"
    
    # 5. Render Navigation Buttons
    _, nav_col, _ = st.columns([1, 6, 1])
    with nav_col:
        # 1. Change columns from 3 to 2
        b1, b2 = st.columns(2, gap="small")
        
        # Helper to create nav buttons
        def create_nav_btn(col, label, key, target_tab):
            with col:
                cls = 'tab-btn-active' if st.session_state.active_tab == target_tab else 'tab-btn'
                st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
                if st.button(label, key=key, use_container_width=True):
                    st.session_state.active_tab = target_tab
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # 2. Only render these two buttons
        create_nav_btn(b1, "🌱 Beginner", "btn_beg", "beginner")
        create_nav_btn(b2, "🚀 Reinvestor", "btn_pro", "pro")

    # 6. Render Content Based on State
    _, content_col, _ = st.columns([1, 6, 1])
    with content_col:
        if st.session_state.active_tab == "beginner":
            render_beginner_zone(assets)
        elif st.session_state.active_tab == "pro":
            render_reinvestor_zone(assets)
        else:
            render_checklist_zone(assets)

    # 7. Bottom Navigation
    st.write(""); st.write("")
    _, mid, _ = st.columns([5, 1.5, 5])
    with mid:
        if st.button("⬅ Dashboard", key="btm_nav", use_container_width=True):
            st.switch_page("app.py")

    st.markdown("<p class='footer-text'>© 2025 Smart Investor Assistant</p>", unsafe_allow_html=True)

# ==============================================================================
# 4. CSS STYLING
# ==============================================================================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    
    /* Global Cleanup */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], footer, #MainMenu { display: none; }
    
    body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%);
        font-family: 'Outfit', sans-serif !important;
        overflow-x: hidden;
    }

    /* Animation Area */
    .area { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; overflow: hidden; }
    .circles { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; margin: 0; padding: 0; }
    .circles li { position: absolute; display: block; list-style: none; width: 20px; height: 20px; background: rgba(255, 255, 255, 0.4); animation: animate 25s linear infinite; bottom: -150px; border-radius: 20%; }
    .circles li:nth-child(1){ left: 25%; width: 80px; height: 80px; animation-delay: 0s; }
    .circles li:nth-child(2){ left: 10%; width: 20px; height: 20px; animation-delay: 2s; animation-duration: 12s; }
    .circles li:nth-child(3){ left: 70%; width: 20px; height: 20px; animation-delay: 4s; }
    .circles li:nth-child(4){ left: 40%; width: 60px; height: 60px; animation-delay: 0s; animation-duration: 18s; }
    @keyframes animate { 0%{ transform: translateY(0) rotate(0deg); opacity: 1; border-radius: 0; } 100%{ transform: translateY(-1000px) rotate(720deg); opacity: 0; border-radius: 50%; } }

    /* Hero */
    .hero-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; padding: 3rem 0; position: relative; z-index: 2; }
    .hero-title { font-size: 4rem; font-weight: 900; margin-bottom: 0.5rem; background: linear-gradient(to right, #30CFD0 0%, #330867 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-subtitle { font-size: 1.3rem; color: #475569; font-weight: 600; margin-bottom: 0.5rem; }
    .hero-desc { color: #64748b; font-size: 1rem; font-style: italic; max-width: 600px; }

    /* Tabs */
    .tab-btn button, .tab-btn-active button { width: 100% !important; border-radius: 12px !important; padding: 0.8rem 1rem !important; font-weight: 700 !important; border: none !important; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important; z-index: 2; position: relative; }
    .tab-btn button { background: linear-gradient(135deg, #475569 0%, #1e293b 100%) !important; color: white !important; opacity: 0.85; }
    .tab-btn-active button { background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important; box-shadow: 0 0 20px rgba(16, 185, 129, 0.5) !important; border: 2px solid #a7f3d0 !important; transform: scale(1.02); color: white !important; opacity: 1; }
    .tab-btn button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important; }
    
    /* Content Boxes */
    .glass-container { background: rgba(255, 255, 255, 0.55); backdrop-filter: blur(16px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.6); border-radius: 20px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.05); z-index: 1; position: relative; }
    .sub-header { font-size: 1.5rem; font-weight: 800; color: #1e293b; margin-top: 1rem; margin-bottom: 1rem; display: inline-block; }
    
    /* Expanders - REDUCED PADDING */
    .streamlit-expanderHeader { background-color: rgba(255, 255, 255, 0.6) !important; border-radius: 12px !important; font-weight: 600 !important; color: #1f2a44 !important; border: 1px solid rgba(255,255,255,0.5) !important; }
    .streamlit-expanderContent { background-color: rgba(255, 255, 255, 0.4) !important; border-radius: 0 0 12px 12px !important; padding: 0.5rem !important; border-top: none; }
    
    /* Bottom Nav */
    div.stButton:last-of-type > button { padding: 0.4rem 1rem !important; font-size: 0.8rem !important; border-radius: 50px !important; background: rgba(24, 40, 72, 0.8) !important; color: white !important; box-shadow: none !important; position: relative; z-index: 2; }
    div.stButton:last-of-type > button:hover { background: #2563eb !important; transform: translateY(-2px); }
    .footer-text { text-align: center; font-size: 0.85rem; opacity: 0.8; margin-top: 4rem; margin-bottom: 2rem; color: #64748b; font-weight: 500; position: relative; z-index: 2;}
    </style>
    
    <div class="area" ><ul class="circles"><li></li><li></li><li></li><li></li><li></li><li></li><li></li><li></li><li></li><li></li></ul></div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()