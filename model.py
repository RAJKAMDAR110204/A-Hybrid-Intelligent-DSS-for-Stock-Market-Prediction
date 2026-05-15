import yfinance as yf
import pandas as pd
import ta
import streamlit as st

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

@st.cache_data
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(period="2y", interval="1d")
    
    df['Return'] = df['Close'].pct_change()
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA10'] = df['Close'].rolling(10).mean()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    
    df = df.dropna()
    return df


def train_model(df):
    df = df.copy()
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()
    
    X = df[['Return', 'MA5', 'MA10', 'RSI']]
    y = df['Target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # FIX: Calmer model. No max_depth=10 memory cheating.
    model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=5, random_state=42)
    model.fit(X_train, y_train)
    
    # FIX: Return actual training accuracy for the UI
    train_accuracy = model.score(X_train, y_train)
    
    return model, train_accuracy

def backtest_model(model, df):

    correct = 0
    total = 0

    # FIX: Only backtest on the last 20% (unseen data)
    test_size = int(len(df) * 0.2)
    test_start = len(df) - test_size

    for i in range(test_start, len(df)-1):
        sample = df[['Return','MA5','MA10','RSI']].iloc[i:i+1]
        pred = model.predict(sample)

        actual = 1 if df['Close'].iloc[i+1] > df['Close'].iloc[i] else 0

        if pred == actual:
            correct += 1

        total += 1

    return correct / total if total > 0 else 0