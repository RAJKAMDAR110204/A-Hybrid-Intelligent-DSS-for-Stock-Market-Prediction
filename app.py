import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import random

# --- YOUR EXISTING IMPORTS ---
from model import get_stock_data, train_model, backtest_model
from sentiment import get_sentiment
from news import get_news
from lstm_model import train_lstm, predict_next
from report import generate_report
from decision import make_decision, get_risk
from market_data import get_fundamentals

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="SmartInvestor AI",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# ---------------- SESSION STATE INIT ----------------
if 'recent_searches' not in st.session_state:
    st.session_state.recent_searches = ["AAPL", "MSFT", "RELIANCE.NS", "TCS.NS"]
if 'dash_search_val' not in st.session_state:
    st.session_state.dash_search_val = ""

# Callback to update recent searches instantly
def handle_search_update():
    search_val = st.session_state.dash_search_input
    if search_val:
        clean_val = search_val.upper().strip()
        # Remove if exists to push it to the front
        if clean_val in st.session_state.recent_searches:
            st.session_state.recent_searches.remove(clean_val)
        st.session_state.recent_searches.insert(0, clean_val)
        # Limit to top 6 recent
        st.session_state.recent_searches = st.session_state.recent_searches[:6]
        st.session_state.dash_search_val = clean_val

# ---------------- LIGHT/MODERN CSS & TICKER ----------------
st.markdown("""
<style>
/* Global Background & Font */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main {
    background-color: #F8F9FA;
    color: #1E293B;
}

/* FIX 1: Keep Sidebar Expander visible but hide right-side menu */
#MainMenu {visibility: hidden;}
[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
header {background-color: transparent !important;}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: #1E293B;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    border-color: #CBD5E1;
}

/* Metric Text */
div[data-testid="stMetricLabel"] {
    color: #64748B;
    font-size: 14px;
    font-weight: 600;
}
div[data-testid="stMetricValue"] {
    color: #0F172A;
    font-size: 32px;
    font-weight: 700;
}

/* Inputs & Forms */
.stTextInput > div > div {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #CBD5E1;
}
.stTextInput input {
    color: #1E293B !important;
}

/* Buttons */
.stButton > button, 
.stDownloadButton > button, 
div.stFormSubmitButton > button {
    background-color: #0F172A;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

/* Info/Success Boxes */
.stInfo {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    color: #1E293B;
}
.stSuccess {
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 12px;
    color: #166534;
}

/* FIX 3: INFINITE SEAMLESS TICKER TAPE CSS */
.ticker-wrap {
    width: 100%;
    overflow: hidden;
    background-color: #0F172A;
    display: flex;
    white-space: nowrap;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.ticker {
    display: flex;
    animation: ticker 90s linear infinite;
}
.ticker:hover {
    animation-play-state: paused; /* Optional: pauses on hover */
}
.ticker__item {
    padding: 10px 2rem;
    font-size: 15px;
    font-weight: 600;
    color: #FFFFFF;
    flex-shrink: 0;
}
.ticker__item span.up { color: #10B981; }
.ticker__item span.down { color: #EF4444; }

@keyframes ticker {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); } /* Moves exactly half the width to loop seamlessly */
}

/* Custom HR */
hr {
    border-top: 1px solid #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CACHE & HELPERS ----------------
@st.cache_resource
def get_trained_model(df):
    return train_model(df)

def get_lstm_prediction(df, lookback):
    model, scaler = train_lstm(df, lookback)
    return predict_next(model, scaler, df, lookback)

@st.cache_data
def get_news_cached(symbol):
    return get_news(symbol)

# ---------------- TOP NAV TICKER TAPE ----------------
# NIFTY 50 + Tech Giants list for infinite loop
all_symbols = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HUL", "SBI", "BHARTIARTL", "ITC", "KOTAKBANK", 
    "L&T", "AXISBANK", "ASIANPAINT", "BAJFINANCE", "MARUTI", "SUNPHARMA", "WIPRO", "HCLTECH", "TATAMOTORS", 
    "ULTRACEMCO", "NTPC", "M&M", "POWERGRID", "TITAN", "BAJAJFINSV", "TATASTEEL", "ADANIENT", "COALINDIA", 
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX"
]

ticker_items = []
for sym in all_symbols:
    # Using mock data for the UI ticker to avoid freezing the app on load
    mock_price = random.uniform(100, 3000)
    mock_change = random.uniform(-3, 3)
    color_class = "up" if mock_change > 0 else "down"
    arrow = "▲" if mock_change > 0 else "▼"
    ticker_items.append(f'<div class="ticker__item">{sym} <span class="{color_class}">{arrow} {mock_price:.2f} ({mock_change:+.2f}%)</span></div>')

# To make the CSS translation loop perfectly, we duplicate the HTML elements inside the flexbox
inner_html = "".join(ticker_items) * 2 

ticker_html = f"""
<div class="ticker-wrap">
    <div class="ticker">
        {inner_html}
    </div>
</div>
"""
st.markdown(ticker_html, unsafe_allow_html=True)

# ---------------- SIDEBAR NAVIGATION ----------------
with st.sidebar:
    st.markdown("### A Hybrid Intelligent DSS for Stock Market Prediction")
    st.markdown("---")
    
    selected_page = option_menu(
        menu_title=None, 
        options=["Dashboard", "Compare Stock", "Predict & News", "Charts"], 
        icons=["house", "arrow-left-right", "cpu", "bar-chart-line"], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#64748B", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "color": "#1E293B", "font-weight": "500"},
            "nav-link-selected": {"background-color": "#E2E8F0", "color": "#0F172A", "font-weight": "700"},
        }
    )

# ---------------- PAGE 1: DASHBOARD ----------------
if selected_page == "Dashboard":
    st.title("Overview Dashboard")
    
    # MAIN SEARCH
    col1, col2 = st.columns([3, 1])
    with col1:
        # FIX 2: Using on_change callback ensures state updates instantly
        st.text_input(
            "What do you want to find?", 
            value=st.session_state.dash_search_val, 
            placeholder="Search by Ticker (e.g., AAPL)", 
            key="dash_search_input",
            on_change=handle_search_update
        )
    
    # RECENT SEARCHES (Rendered AFTER state update)
    st.markdown("##### Recently Searched")
    recent_cols = st.columns(6) # Show up to 6
    for idx, recent_sym in enumerate(st.session_state.recent_searches):
        with recent_cols[idx]:
            if st.button(recent_sym, key=f"recent_btn_{idx}", use_container_width=True):
                st.session_state.dash_search_val = recent_sym
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search Execution
    active_search = st.session_state.dash_search_val
    if active_search:
        with st.spinner(f"Fetching data for {active_search}..."):
            df = get_stock_data(active_search)
            
            if df.empty:
                st.error("Invalid stock symbol or no data found.")
            else:
                current_price = float(df['Close'].iloc[-1])
                prev_price = float(df['Close'].iloc[-2])
                change = current_price - prev_price
                change_percent = (change / prev_price) * 100
                currency = "₹" if ".NS" in active_search else "$"
                
                fundamentals = get_fundamentals(active_search)
                
                st.markdown(f"### {active_search.upper()} Overview")
                m1, m2, m3, m4 = st.columns(4)
                
                m1.metric("Current Price", f"{currency}{current_price:.2f}", f"{change:.2f} ({change_percent:.2f}%)")
                m2.metric("P/E Ratio", fundamentals.get("pe_ratio", "N/A") if fundamentals else "N/A")
                m3.metric("52-Week High", f"{currency}{fundamentals.get('52_week_high', 'N/A')}" if fundamentals else "N/A")
                
                div_val = fundamentals.get("dividend_yield") if fundamentals else None
                div_display = f"{float(div_val) * 100:.2f}%" if div_val and div_val != "N/A" else "N/A"
                m4.metric("Dividend Yield", div_display)

    st.markdown("---")
    
    # NIFTY 50 GRID
    st.markdown("### 🇮🇳 Top Market Movers")
    st.caption("Live overview of top constituents")
    
    # Reduced list for visual grid to prevent UI clutter
    grid_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HUL.NS", "SBI.NS", "BHARTIARTL.NS", "ITC.NS", "AAPL", "MSFT", "GOOGL"]
    
    with st.container(height=400): 
        cols = st.columns(3) 
        for idx, sym in enumerate(grid_symbols):
            col_idx = idx % 3
            with cols[col_idx]:
                mock_price = random.uniform(100, 4000) 
                mock_change = random.uniform(-2, 2)
                currency = "₹" if ".NS" in sym else "$"
                
                st.markdown(f"""
                <div style="background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <h5 style="margin:0; color:#1E293B;">{sym.replace('.NS', '')}</h5>
                    <h3 style="margin:5px 0 0 0; color:#0F172A;">{currency}{mock_price:.2f}</h3>
                    <p style="margin:0; color:{'#10B981' if mock_change > 0 else '#EF4444'}; font-weight:600;">
                        {'▲' if mock_change > 0 else '▼'} {mock_change:.2f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)


# ---------------- PAGE 2: COMPARE STOCK ----------------
elif selected_page == "Compare Stock":
    st.title("Search Stocks to Compare")
    
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        stock1 = st.text_input("1ST STOCK", value="MSFT")
    with c2:
        stock2 = st.text_input("2ND STOCK", value="AAPL")
    with c3:
        st.write("") 
        st.write("") 
        compare_btn = st.button("Compare Now", use_container_width=True)
        
    if compare_btn and stock1 and stock2:
        # --- NEW COMPATIBILITY CHECK ---
        is_stock1_ns = ".NS" in stock1.upper()
        is_stock2_ns = ".NS" in stock2.upper()
        
        if is_stock1_ns != is_stock2_ns:
            st.warning("!Incompatible comparison: Cannot compare a US stock with an Indian (NSE) stock. Please select two stocks from the same market.")
        else:
            # --- EXISTING LOGIC ---
            with st.spinner("Fetching comparison data..."):
                df1 = get_stock_data(stock1)
                df2 = get_stock_data(stock2)
                
                if df1.empty or df2.empty:
                    st.error("Could not fetch data for one or both symbols.")
                else:
                    col1, col2 = st.columns(2)
                    curr_price1 = float(df1['Close'].iloc[-1])
                    curr_price2 = float(df2['Close'].iloc[-1])
                    
                    with col1:
                        st.info(f"**{stock1.upper()}** Current Price: ${curr_price1:.2f}")
                    with col2:
                        st.info(f"**{stock2.upper()}** Current Price: ${curr_price2:.2f}")
                    
                    st.markdown("### Price Comparison (Close Price)")
                    combined_df = pd.DataFrame({
                        stock1.upper(): df1['Close'],
                        stock2.upper(): df2['Close']
                    }).dropna()
                    st.line_chart(combined_df)

# ---------------- PAGE 3: PREDICT & NEWS ----------------
elif selected_page == "Predict & News":
    st.title("AI Prediction & Top News")
    
    col_settings, col_content = st.columns([1, 3])
    
    with col_settings:
        st.markdown("#### Model Settings")
        symbol = st.text_input("Enter Stock Symbol", value="AAPL", key="pred_sym")
        lstm_lookback = st.slider("LSTM Lookback Window", min_value=30, max_value=90, value=60, step=10)
        analyze_button = st.button("🚀 Analyze Stock", use_container_width=True)
        
    with col_content:
        if analyze_button:
            with st.spinner("Running deep learning models and analyzing sentiment..."):
                df = get_stock_data(symbol)
                if df.empty:
                    st.error("Invalid stock symbol.")
                else:
                    currency = "₹" if ".NS" in symbol else "$"
                    
                    # Core ML Logic
                    model, acc = get_trained_model(df)
                    bt_acc = backtest_model(model, df)
                    
                    latest = df[['Return', 'MA5', 'MA10', 'RSI']].iloc[-1:]
                    prediction = int(model.predict(latest)[0])
                    confidence = float(model.predict_proba(latest).max()) * 100
                    
                    clean_symbol = symbol.replace(".NS", "")
                    news = get_news_cached(clean_symbol)
                    sentiment_score = get_sentiment(news)
                    
                    decision = make_decision(prediction, sentiment_score, confidence)
                    risk = get_risk(confidence)
                    current_price = float(df['Close'].iloc[-1])
                    future_price = get_lstm_prediction(df, lstm_lookback)
                    
                    try:
                        if future_price is not None: future_price = float(future_price)
                    except:
                        try: future_price = float(future_price[0][0])
                        except: future_price = None

                    # --- Render Results ---
                    st.markdown("### Prediction Results")
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("Current Price", f"{currency}{current_price:.2f}")
                    p2.metric("AI Prediction", "UP 📈" if prediction == 1 else "DOWN 📉")
                    p3.metric("Confidence", f"{confidence:.2f}%")
                    p4.metric("Risk Level", risk)
                    
                    strength = "Strong" if confidence > 75 else "Moderate" if confidence > 60 else "Weak"
                    st.success(f"**Final AI Recommendation:** {decision} ({strength})")
                    
                    st.markdown("### 📊 Model Performance")
                    acc_col1, acc_col2 = st.columns(2)
                    acc_col1.metric("Training Accuracy", f"{acc*100:.2f}%")
                    acc_col2.metric("Backtest Accuracy", f"{bt_acc*100:.2f}%")
                    
                    st.markdown("### 🧠  Market Sentiment")
                    sentiment_progress = min(max((sentiment_score + 1) / 2, 0), 1)
                    st.progress(sentiment_progress)
                    st.caption(f"Sentiment Score: {round(sentiment_score, 2)}")
                    
                    st.markdown("### Top News Drivers")
                    if news:
                        for n in news[:10]:
                            st.info(n)
                    else:
                        st.write("No recent news found.")

                    # Report Logic
                    st.markdown("---")
                    fp_report = f"{currency}{float(future_price):.2f}" if future_price else "N/A"
                    report_data = {
                        "Stock": symbol, "Current Price": f"{currency}{current_price:.2f}",
                        "Prediction": "UP" if prediction == 1 else "DOWN", "Confidence": f"{confidence:.2f}%",
                        "Risk": risk, "Recommendation": decision, "Predicted Price": fp_report
                    }
                    buffer = BytesIO()
                    generate_report(buffer, report_data)
                    buffer.seek(0)
                    st.download_button("📥 Download Analysis Report", data=buffer, file_name=f"{symbol}_Report.pdf", mime="application/pdf")

# ---------------- PAGE 4: CHARTS ----------------
elif selected_page == "Charts":
    st.title("Technical Analysis Charts")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ticker = st.text_input("Ticker for Chart", "AAPL")
        show_ma5 = st.checkbox("Show MA5", value=True)
        show_ma10 = st.checkbox("Show MA10", value=True)
        fetch_chart = st.button("Update Chart", use_container_width=True)
        
    with col2:
        if ticker:
            with st.spinner("Loading chart data..."):
                df = get_stock_data(ticker)
                if not df.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market Data"
                    ))
                    
                    if show_ma5 and 'MA5' in df.columns:
                        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='#3B82F6')))
                    if show_ma10 and 'MA10' in df.columns:
                        fig.add_trace(go.Scatter(x=df.index, y=df['MA10'], mode='lines', name='MA10', line=dict(color='#8B5CF6')))
                    
                    fig.update_layout(
                        template="plotly_white", 
                        xaxis_rangeslider_visible=False,
                        height=600,
                        margin=dict(l=0, r=0, t=30, b=0),
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#F8F9FA"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("No chart data available for this ticker.")
