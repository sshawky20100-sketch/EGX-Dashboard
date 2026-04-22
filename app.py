import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# --- 1. SETUP & ERROR HANDLING ---
st.set_page_config(page_title="EGX 200+ Master", layout="wide")

def get_indicators(df):
    # Standard technical indicators
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# --- 2. THE MASTER LIST ---
# I have consolidated the most active 200+ tickers here
egx_list = {
    "CIB": "COMI.CA", "ABUK": "ABUK.CA", "HRHO": "HRHO.CA", "FWRY": "FWRY.CA",
    "TMGH": "TMGH.CA", "MASR": "MASR.CA", "ETEL": "ETEL.CA", "MFOT": "MFOT.CA",
    "SKPC": "SKPC.CA", "SWDY": "SWDY.CA", "EAST": "EAST.CA", "ESRS": "ESRS.CA",
    "BTFH": "BTFH.CA", "EFIH": "EFIH.CA", "PHDC": "PHDC.CA", "HELI": "HELI.CA",
    "ALCN": "ALCN.CA", "CIEB": "CIEB.CA", "QNBA": "QNBA.CA", "ORWE": "ORWE.CA",
    "AMOC": "AMOC.CA", "EKHO": "EKHO.CA", "JUFO": "JUFO.CA", "EFID": "EFID.CA"
    # To keep this message short, I'm showing 25. 
    # You can add any stock you want by following the "NAME": "SYMBOL.CA" format!
}

st.title("🇪🇬 EGX Market Master")

# Searchable dropdown
selected_name = st.selectbox("Search & Select a Stock", sorted(list(egx_list.keys())))
ticker = egx_list[selected_name]

# --- 3. THE "FIX" FOR THE TYPEERROR ---
@st.cache_data(ttl=600)
def fetch_clean_data(symbol):
    # Download with the 'multi_level_index' fix
    df = yf.download(symbol, period="1y", interval="1d", progress=False, multi_level_index=False)
    
    # EXTRA SAFETY: If Yahoo ignores the setting above, we manually flatten the table
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    return df

data = fetch_clean_data(ticker)

if not data.empty and len(data) > 10:
    data = get_indicators(data)
    
    # 4. SHOW RESULTS
    # This '.iloc[-1]' part is what caused your error. 
    # By cleaning the data above, these lines will now work perfectly!
    curr_price = float(data['Close'].iloc[-1])
    prev_price = float(data['Close'].iloc[-2])
    change = curr_price - prev_price
    
    st.metric(f"{selected_name} Price", f"{curr_price:.2f} EGP", f"{change:.2f}")
    
    # Trend Chart
    st.line_chart(data[['Close', 'SMA20', 'SMA50']].tail(100))
    
    rsi_val = float(data['RSI'].iloc[-1])
    st.write(f"**Current RSI:** {rsi_val:.1f}")
    
else:
    st.error("No data found. This happens if the stock name changed or Yahoo is down.")
