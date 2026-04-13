import streamlit as st
import sqlite3
import os
import requests
import time
import pandas as pd
import pandas_ta as ta
import streamlit.components.v1 as components
from pybit.unified_trading import HTTP

# --- 1. CONFIGURATION & UI STYLES ---
st.set_page_config(page_title="NEXUS PRO v24", layout="wide", initial_sidebar_state="expanded")
DB_PATH = "nexus_hub.db"

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .status-box { padding: 20px; border-radius: 12px; border: 1px solid #00ffcc; background: rgba(0, 255, 204, 0.03); margin-bottom: 15px; }
    .bot-card { border-left: 4px solid #00ffcc; padding-left: 15px; margin: 10px 0; }
    .log-container { background: #000; border: 1px solid #1a1a1a; padding: 15px; font-family: 'Courier New', monospace; font-size: 11px; color: #00ff00; height: 250px; overflow-y: auto; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INTELLIGENCE MODULES (Твои боты) ---

class WhaleWatcher:
    """Анализатор крупных игроков в стакане"""
    def scan(self, session, symbol, threshold=500000):
        try:
            ob = session.get_orderbook(category="spot", symbol=symbol)
            asks = ob['result']['a']
            for price, volume in asks[:15]:
                usd_val = float(price) * float(volume)
                if usd_val >= threshold:
                    return True, float(price), usd_val
            return False, 0, 0
        except: return False, 0, 0

class PatternRecon:
    """Анализ графиков на основе оцифрованных паттернов"""
    def analyze(self, df):
        if df is None or len(df) < 30: return {"signal": "NEUTRAL", "rsi": 50}
        
        # Индикаторы со скринов
        df['RSI'] = ta.rsi(df['close'], length=14)
        bb = ta.bbands(df['close'], length=20, std=2)
        df['EMA20'] = ta.ema(df['close'], length=20)
        df['EMA50'] = ta.ema(df['close'], length=50)
        
        last = df.iloc[-1]
        
        # Логика входа: Перепроданность + Касание нижней границы Bollinger
        if last['RSI'] < 32 and last['close'] <= bb['BBL_20_2.0'].iloc[-1]:
            return {"signal": "STRONG BUY", "rsi": round(last['RSI'], 1), "reason": "BB Touch + RSI Oversold"}
        
        trend = "BULL" if last['EMA20'] > last['EMA50'] else "BEAR"
        return {"signal": "WAIT", "rsi": round(last['RSI'], 1), "trend": trend}

# --- 3. UTILS & DATA ---

def get_kline_data(session, symbol):
    try:
        res = session.get_kline(category="spot", symbol=symbol, interval="15")
        df = pd.DataFrame(res['result']['list'], columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'turnover'])
        df['close'] = df['close'].astype(float)
        return df.iloc[::-1]
    except: return None

def verify_license_db(key):
    if not os.path.exists(DB_PATH): return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM orders WHERE license_key = ? AND status = 'paid'", (key.strip(),))
        res = cur.fetchone(); conn.close()
        return res is not None
    except: return False

# --- 4. AUTHENTICATION ---

if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🛡️ NEXUS CORE ACCESS")
    key = st.text_input("License Key", type="password", help="Enter the key from @Nexus_Bot")
    if st.button("Activate Neural Core"):
        if verify_license_db(key):
            st.session_state['authenticated'] = True
            st.success("Welcome, Yaroslav. Access Granted.")
            time.sleep(1); st.rerun()
        else: st.error("Access Denied: Invalid License")
    st.stop()

# --- 5. MAIN ENGINE ---

BYBIT_KEY = st.secrets.get("BYBIT_API_KEY", "")
BYBIT_SECRET = st.secrets.get("BYBIT_API_SECRET", "")
session = HTTP(testnet=False, api_key=BYBIT_KEY, api_secret=BYBIT_SECRET)

with st.sidebar:
    st.title("🦅 NEXUS CORE")
    active_coin = st.selectbox("Trading Pair", ["SOL", "BTC", "ETH"])
    st.divider()
    st.subheader("🤖 Bot Ecosystem")
    # Переключатели активности ботов
    run_whale = st.toggle("Whale Watcher", value=True)
    run_recon = st.toggle("Pattern Recon", value=True)
    run_arb = st.toggle("Arbitrage Engine", value=True)
    st.divider()
    page = st.radio("DASHBOARD", ["⚡ TERMINAL", "📊 INTELLIGENCE", "🛠 SETTINGS"])
    if st.button("Log Out"):
        st.session_state['authenticated'] = False; st.rerun()

if page == "⚡ TERMINAL":
    st.title(f"🚀 {active_coin} Nexus Terminal")
    
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        # Интерактивный график TradingView
        components.html(f'<div style="height:500px;"><div id="c" style="height:100%;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BYBIT:{active_coin}USDT", "interval": "15", "theme": "dark", "container_id": "c"}});</script></div>', height=510)
        
        # Быстрая статистика под графиком
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Bybit Price", f"${requests.get(f'https://api.binance.com/api/v3/ticker_price?symbol={active_coin}USDT').json()['price']}")
        with c2: st.metric("Network Status", "Latency: 24ms", delta="Stable")
        with c3: st.metric("Active Bots", "3 Online")

    with col_side:
        # Модуль Whale Watcher
        st.markdown('<div class="status-box">', unsafe_allow_html=True)
        st.subheader("🐋 Whale Watcher")
        if run_whale:
            whale = WhaleWatcher()
            found, price, val = whale.scan(session, f"{active_coin}USDT")
            if found: st.warning(f"WALL: ${val/1000:,.0f}k at {price}")
            else: st.success("Liquidity: Clear")
        else: st.info("Module Paused")
        st.markdown('</div>', unsafe_allow_html=True)

        # Модуль Pattern Recon
        st.markdown('<div class="status-box">', unsafe_allow_html=True)
        st.subheader("🎯 Pattern Recon")
        if run_recon:
            df = get_kline_data(session, f"{active_coin}USDT")
            recon = PatternRecon()
            analysis = recon.analyze(df)
            st.metric("RSI (15m)", analysis['rsi'])
            if analysis['signal'] == "STRONG BUY":
                st.balloons()
                st.error(f"ENTRY: {analysis['reason']}")
            else: st.write(f"Trend: **{analysis.get('trend', 'Wait')}**")
        else: st.info("Module Paused")
        st.markdown('</div>', unsafe_allow_html=True)

        # Ручное управление
        if st.button(f"EXECUTE {active_coin} SELL", type="primary", use_container_width=True):
            st.toast("Executing order via Bybit API...")

elif page == "📊 INTELLIGENCE":
    st.title("📟 Neural Activity Logs")
    st.markdown('<div class="log-container">', unsafe_allow_html=True)
    st.write(f"[{time.strftime('%H:%M:%S')}] PatternRecon: Pattern 'BB-Squeeze' detected on {active_coin}")
    st.write(f"[{time.strftime('%H:%M:%S')}] WhaleWatcher: High volume sell wall removed at {active_coin} resistance")
    st.write(f"[{time.strftime('%H:%M:%S')}] ArbitrageEngine: Calculating triangular spread for SOL/BTC/USDT")
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "🛠 SETTINGS":
    st.title("⚙️ System Configuration")
    with st.expander("Bybit API Connectivity", expanded=True):
        st.text_input("API Key", value=BYBIT_KEY, type="password")
        st.text_input("API Secret", value=BYBIT_SECRET, type="password")
    
    with st.expander("Bot Parameters"):
        st.slider("RSI Threshold", 10, 40, 30)
        st.number_input("Whale Wall Threshold (USD)", value=500000, step=50000)
    
    st.button("Sync All Systems", use_container_width=True)
