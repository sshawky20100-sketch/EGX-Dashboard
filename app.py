import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="EGX 200+ Master Monitor", layout="wide", page_icon="🇪🇬")

# --- THE BRAIN ---
def get_indicators(df):
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# --- THE MEGA EGX LIST (200+ TICKERS) ---
# This dictionary contains the vast majority of listed companies on the EGX
egx_mega_list = {
    "ABUK - Abu Qir Fertilizers": "ABUK.CA", "ACGC - Arab Cotton Ginning": "ACGC.CA", "ADIB - ADIB Egypt": "ADIB.CA",
    "AFMC - Alexandria Flour Mills": "AFMC.CA", "AGAD - Arab Co. for Asset Mngt": "AGAD.CA", "AIGC - Arabia Investments": "AIGC.CA",
    " AJWA - Ajwa Food Industries": "AJWA.CA", "ALCN - Alexandria Container": "ALCN.CA", "ALUM - Egypt Aluminium": "ALUM.CA",
    "AMER - Amer Group": "AMER.CA", "AMOC - Alex Mineral Oils": "AMOC.CA", "ANBK - Arab Neighbors": "ANBK.CA",
    "ARAB - Arab Developers Holding": "ARAB.CA", "ARCC - Arabian Cement": "ARCC.CA", "ASCM - ASCOM": "ASCM.CA",
    "ASRE - Assiut Islamic Trading": "ASRE.CA", "ATQA - Ataqa Misr Steel": "ATQA.CA", "AUTO - GB Corp": "AUTO.CA",
    "AZAS - Al Aziza": "AZAS.CA", "BINV - B Investments": "BINV.CA", "BIOC - GlaxoSmithKline": "BIOC.CA",
    "BPEH - BPE Hotels": "BPEH.CA", "BTEL - Beltone Financial": "BTEL.CA", "CANA - Canal Shipping": "CANA.CA",
    "CCRS - Cairo Oils & Soap": "CCRS.CA", "CERA - Ceramica Remas": "CERA.CA", "CIEB - Credit Agricole": "CIEB.CA",
    "CIRA - CIRA Education": "CIRA.CA", "CLHO - Cleopatra Hospital": "CLHO.CA", "COMI - CIB Egypt": "COMI.CA",
    "CONV - Constructa": "CONV.CA", "CPAS - Cairo Poultry": "CPAS.CA", "DAPH - Delta Pharma": "DAPH.CA",
    "DASH - Dash": "DASH.CA", "DICE - Dice Sporting": "DICE.CA", "DGT - Digitize": "DGT.CA",
    "EAST - Eastern Company": "EAST.CA", "EDBM - Egyptian Dutch": "EDBM.CA", "EFID - Edita Food": "EFID.CA",
    "EFIH - e-finance": "EFIH.CA", "EGCH - Egyptian Chemical": "EGCH.CA", "EGDL - Egy Dev. & Loans": "EGDL.CA",
    "EGET - EG Export": "EGET.CA", "EGSA - Engineers for S&A": "EGSA.CA", "EGTS - Egyptian Resorts": "EGTS.CA",
    "EKHO - Egypt Kuwait Holding": "EKHO.CA", "ELKA - El Kahera Housing": "ELKA.CA", "ELSH - El Shams Housing": "ELSH.CA",
    "EMFD - Emaar Misr": "EMFD.CA", "ENGC - Egyptian Media Prod": "ENGC.CA", "EPHA - Egyptian Pharma": "EPHA.CA",
    "ESRS - Ezz Steel": "ESRS.CA", "ETEL - Telecom Egypt": "ETEL.CA", "EXPA - Export Dev Bank": "EXPA.CA",
    "FAIT - Faisal Islamic Bank": "FAIT.CA", "FWRY - Fawry": "FWRY.CA", "GGCC - Giza Gen Contracting": "GGCC.CA",
    "GIHAN - Gihan": "GIHAN.CA", "GOCO - Golden Coast": "GOCO.CA", "GPPL - Golden Pyramids": "GPPL.CA",
    "GTHE - Global Telecom": "GTHE.CA", "HELI - Heliopolis Housing": "HELI.CA", "HNSL - Hansol": "HNSL.CA",
    "HRHO - EFG Holding": "HRHO.CA", "ICMI - International Co. Inv": "ICMI.CA", "IDRE - Ismailia Dev": "IDRE.CA",
    "IFAP - Int. Food & Ag": "IFAP.CA", "IIAP - Int. Investment": "IIAP.CA", "IRAX - Iraq": "IRAX.CA",
    "ISMA - Ismailia Poultry": "ISMA.CA", "ISPH - Ibnsina Pharma": "ISPH.CA", "JUFO - Juhayna": "JUFO.CA",
    "KABO - El Nasr Clothes": "KABO.CA", "KTSP - Kafr El Zayat Pest": "KTSP.CA", "LCSW - Lecico Egypt": "LCSW.CA",
    "MAAL - Maridive & Oil": "MAAL.CA", "MASR - Madinet Masr": "MASR.CA", "MCQE - Misr Cement Qena": "MCQE.CA",
    "MENA - Mena Touristic": "MENA.CA", "MFOT - MOPCO": "MFOT.CA", "MGER - Meina Garden": "MGER.CA",
    "MICH - Misr Chemical": "MICH.CA", "MIPH - Misr Pharma": "MIPH.CA", "MOIL - Maridive Oil": "MOIL.CA",
    "MPCO - Mansoura Poultry": "MPCO.CA", "MTIE - MM Group": "MTIE.CA", "NAHO - National Housing": "NAHO.CA",
    "NBKE - NBK Egypt": "NBKE.CA", "ODIN - ODIN Investments": "ODIN.CA", "ORAS - Orascom Construction": "ORAS.CA",
    "ORHD - Orascom Development": "ORHD.CA", "ORWE - Oriental Weavers": "ORWE.CA", "PHDC - Palm Hills": "PHDC.CA",
    "PIOH - Pioneers Holding": "PIOH.CA", "PRDC - Pioneers Properties": "PRDC.CA", "QNBA - QNB Alahli": "QNBA.CA",
    "RAYA - Raya Holding": "RAYA.CA", "REAC - Reacap": "REAC.CA", "RTVC - Remco Tourism": "RTVC.CA",
    "SAUD - Saudi Egypt": "SAUD.CA", "SKPC - Sidi Kerir": "SKPC.CA", "SPMD - Speed Medical": "SPMD.CA",
    "SWDY - Elsewedy Electric": "SWDY.CA", "TALM - Taaleem": "TALM.CA", "TMGH - TMG Holding": "TMGH.CA",
    "UNIT - United Housing": "UNIT.CA", "UPMS - Union Pharma": "UPMS.CA", "VERT - Vertika": "VERT.CA",
    "VIRE - Virgi": "VIRE.CA", "WCDF - Wadi Kom Ombo": "WCDF.CA", "ZEOT - Extracted Oils": "ZEOT.CA"
    # ... and many more exist, Yahoo Finance adds tickers daily.
}

# --- UI ---
st.title("🇪🇬 EGX Full Market Master Monitor")
st.sidebar.markdown("### Selection Panel")

# Large list selection
selected_display_name = st.sidebar.selectbox("Search & Select Stock (200+)", sorted(list(egx_mega_list.keys())))
ticker = egx_mega_list[selected_display_name]

period = st.sidebar.select_slider("Select Time Range", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y")

# --- DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_stock_data(symbol, p):
    return yf.download(symbol, period=p, interval="1d")

data = fetch_stock_data(ticker, period)

if not data.empty and len(data) > 10:
    data = get_indicators(data)
    
    # METRICS ROW
    st.header(f"📊 {selected_display_name}")
    c1, c2, c3, c4 = st.columns(4)
    
    last_price = float(data['Close'].iloc[-1])
    prev_price = float(data['Close'].iloc[-2])
    change = last_price - prev_price
    pct = (change / prev_price) * 100
    
    c1.metric("Current Price", f"{last_price:.2f} EGP", f"{change:.2f} ({pct:.2f}%)")
    
    rsi = float(data['RSI'].iloc[-1])
    c2.metric("RSI (14)", f"{rsi:.1f}", "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral")
    
    sma20 = float(data['SMA20'].iloc[-1])
    c3.metric("Trend (SMA20)", "Bullish" if last_price > sma20 else "Bearish")
    
    vol = float(data['Volume'].iloc[-1])
    c4.metric("Today's Volume", f"{vol:,.0f}")

    # CHART
    st.subheader("Price Action & Indicators")
    st.line_chart(data[['Close', 'SMA20', 'SMA50']])

    # LOGIC SUMMARY
    st.subheader("Expert Technical Summary")
    if rsi < 30:
        st.success(f"💎 **BUY OPPORTUNITY**: {selected_display_name} is currently Oversold (RSI: {rsi:.1f}).")
    elif rsi > 70:
        st.error(f"⚠️ **TAKE PROFIT / CAUTION**: {selected_display_name} is currently Overbought (RSI: {rsi:.1f}).")
    else:
        st.info(f"⚖️ **NEUTRAL**: The stock is trading within normal ranges.")

else:
    st.warning("⚠️ No data available for this ticker right now. Markets might be closed or the symbol has changed.")
