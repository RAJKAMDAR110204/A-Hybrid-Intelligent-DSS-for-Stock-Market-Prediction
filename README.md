# SmartInvestor AI - Stock Analysis Platform

An advanced AI-powered financial intelligence platform for stock analysis and recommendations.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure all packages are installed correctly:
```bash
python -c "from model import *; from sentiment import *; from news import *; from lstm_model import *; from report import *; from decision import *; from market_data import *; print('All dependencies ready!')"
```

## Running the Application

Start the Streamlit web app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

- **AI Stock Analysis**: Uses Random Forest ML model for price prediction
- **LSTM Neural Network**: Advanced deep learning model for future price forecasting
- **Sentiment Analysis**: Analyzes market sentiment from news articles
- **News Integration**: Fetches latest financial news and headlines
- **Company Fundamentals**: Displays P/E ratios, dividend yields, and 52-week data
- **Risk Assessment**: Calculates risk levels based on model confidence
- **PDF Reports**: Download detailed analysis reports
- **Interactive Charts**: Real-time candlestick charts with moving averages

## How to Use

1. Enter a stock symbol (e.g., `AAPL` for USA stocks or `RELIANCE.NS` for Indian stocks)
2. Adjust LSTM lookback window (default 60 days)
3. Click "Analyze Stock"
4. View predictions, sentiment scores, and company fundamentals
5. Download analysis report as PDF

## Supported Markets

- **USA**: Standard stock tickers (AAPL, GOOGL, MSFT, etc.)
- **India**: NSE tickers with `.NS` suffix (RELIANCE.NS, TCS.NS, etc.)

## Technology Stack

- **Frontend**: Streamlit
- **ML Models**: Scikit-learn (Random Forest), TensorFlow/Keras (LSTM)
- **Data**: yfinance, News API
- **NLP**: VADER Sentiment Analysis
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

## Notes

- The app requires internet connection to fetch stock data and news
- API keys for news and fundamentals are pre-configured
- First run may take longer due to model training
