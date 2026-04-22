import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple

# --- PART 1: THE BRAIN (Math Functions) ---

def compute_sma(series, window):
    return series.rolling(window=window, min_periods=1).mean()

def compute_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=window, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def compute_bollinger_bands(series, window=20, num_std=2.0):
    sma = compute_sma(series, window)
    std = series.rolling(window=window, min_periods=1).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower

def compute_all_indicators(df):
    df = df.copy().sort_values("date").reset_index(drop=True)
    close = df["close"]
    df["sma_20"] = compute_sma(close, 20)
    df["sma_50"] = compute_sma(close, 50)
    df["rsi"] = compute_rsi(close, 14)
    df["macd"], df["macd_signal"], df["macd_hist"] = compute_macd(close)
    df["bb_upper"], df["bb_mid"], df["bb_lower"] = compute_bollinger_bands(close)
    return df

def generate_signal(df):
    if df.empty or len(df) < 30:
        return {"signal": "HOLD", "confidence": 50, "reasons": ["Gathering more market data..."]}
    
    latest = df.iloc[-1]
    score = 0
    reasons = []
    
    if latest['rsi'] < 30:
        score += 2
        reasons.append(f"🟢 RSI is low ({latest['rsi']:.1f}) - Market is oversold.")
    elif latest['rsi'] > 70:
        score -= 2
        reasons.append(f"🔴 RSI is high ({latest['rsi']:.1f}) - Market is overbought.")
        
    if latest['close'] > latest['sma_20']:
        score += 1
        reasons.append("🟢 Price is above the 20-day average (Uptrend).")
    else:
        score -= 1
        reasons.append("🔴 Price is below the 20-day average (Downtrend).")

    signal = "BUY" if score >= 2 else "SELL" if score <= -2 else "HOLD"
    return {"signal": signal, "confidence": 75, "reasons": reasons}

# --- PART 2: THE FACE (Streamlit UI) ---

st.set_page_config(page_title="EGX Technical Dashboard", layout="wide")

st.title("📈 EGX Stock Analysis Dashboard")
st.write("Real-time technical indicators and trading signals.")

# Creating sample data (In the future, you can connect your scraper here)
dates = pd.date_range(start='2024-01-01', periods=100)
prices = np.random.randn(100).cumsum() + 100 
df_sample = pd.DataFrame({
    'date': dates,
    'close': prices,
    'volume': np.random.randint(1000, 5000, 100)
})

# Run the math
processed_df = compute_all_indicators(df_sample)
analysis = generate_signal(processed_df)

# Show the Signal
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Current Signal", value=analysis['signal'])
with col2:
    st.progress(analysis['confidence'] / 100)
    st.write(f"Signal Confidence: {analysis['confidence']}%")

st.subheader("Analysis Summary")
for r in analysis['reasons']:
    st.write(r)

# Show the Chart
st.subheader("Price Trend")
st.line_chart(processed_df.set_index('date')[['close', 'sma_20', 'sma_50']])
