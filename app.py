import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import time

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="EGX Master Monitor", layout="wide")

# --- 2. THE MATH (RELIABLE VERSION) ---
def get_indicators(df):
    try:
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except Exception as e:
        return df

# --- 3. UPDATED TICKER LIST (Active 2026) ---
egx_mega_list = {
    "CIB (Commercial Intl Bank)": "COMI.CA",
    "Abu Qir Fertilizers": "ABUK.CA",
    "EFG Hermes Holding": "HRHO.CA",
    "Fawry Banking": "FWRY.CA",
    "TMG Holding": "TMGH.CA",
    "Madinet Masr (New)": "MASR.CA", # Updated from MNHD
    "Telecom Egypt": "ETEL.CA",
    "MOPCO Fertilizers": "MFOT.CA",
    "Sidi Kerir Petrochemicals": "SKPC.CA",
    "Elsewedy Electric": "SWDY.CA",
    "Eastern Company": "EAST.CA",
    "Ezz Steel": "ESRS.CA",
    "Beltone Financial": "BTFH.CA",
    "E-Finance": "EFIH.CA",
    "Palm Hills Development": "PHDC.CA",
    "Heliopolis Housing": "HELI.CA",
    "Alexandria Containers": "ALCN.CA",
    "Credit Agricole Egypt": "CIEB.CA",
    "QNB Alahli": "QNBA.CA",
    "Oriental Weavers": "ORWE.CA"
    # Note: I've kept the top 20 here for stability. 
    # If a stock fails, it's often due to Yahoo Finance server issues.
}

# --- 4. INTERFACE ---
st.title("🇪🇬 EGX Market Master")

# Sidebar
st.sidebar.header("Settings")
selected_name = st.sidebar.selectbox("Select Stock", sorted(list(egx_mega_list.keys())))
ticker = egx_mega_list[selected_name]

# --- 5. SMART DATA FETCHING ---
@st.cache_data(ttl=600) # Refresh data every 10 minutes
def fetch_data_safe(symbol):
    try:
        # We use a 1-year period to ensure we have enough data for SMA50
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        return df
    except:
        return pd.DataFrame()

with st.spinner(f"Loading {selected_name}..."):
    data = fetch_data_safe(ticker)

if not data.empty and len(data) > 50:
    data = get_indicators(data)
    
    # Show Metrics
    last_p = float(data['Close'].iloc[-1])
    prev_p = float(data['Close'].iloc[-2])
    chg = last_p - prev_p
    
    st.header(f"{selected_name} ({ticker})")
    c1, c2, c3 = st.columns(3)
    c1.metric("Price", f"{last_p:.2f} EGP", f"{chg:.2f}")
    
    rsi = float(data['RSI'].iloc[-1])
    c2.metric("RSI (14)", f"{rsi:.1f}")
    
    status = "Bullish" if last_p > float(data['SMA20'].iloc[-1]) else "Bearish"
    c3.metric("Trend", status)

    # Chart
    st.line_chart(data[['Close', 'SMA20', 'SMA50']].tail(100))

else:
    st.error(f"🔴 Connection Error: Yahoo Finance is not returning data for {ticker} right now.")
    st.info("Try selecting a different stock (like CIB) to see if it's a general connection issue or just this ticker.")
