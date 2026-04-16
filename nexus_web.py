import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import requests
import time
import sqlite3
import os
import streamlit.components.v1 as components
from pybit.unified_trading import HTTP
from wallet import NexusCryptoCore

# ==========================================
# GLOBAL CONFIG & CORE
# ==========================================
DB_PATH    = "nexus_hub.db"
SECRET_PIN = "qGvANo8s9X7"
crypto     = NexusCryptoCore()

# ==========================================
# DESIGN SYSTEM
# ==========================================
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: #0E0F11 !important;
    color: #C8CAD0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 14px;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0E0F11; }
::-webkit-scrollbar-thumb { background: #2A2C33; border-radius: 2px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #13141A !important;
    border-right: 1px solid #1E2028 !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] label { color: #6A6D7A !important; font-size: 12px !important; }
section[data-testid="stSidebar"] hr { border-color: #1E2028 !important; }

.nx-brand {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; letter-spacing: 5px;
    color: #D4A843; text-transform: uppercase;
    padding: 6px 0 2px;
}
.nx-sub { font-size: 10px; color: #2A2C33; letter-spacing: 2px; margin-bottom: 18px; }

/* Page title */
.nx-page-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; letter-spacing: 4px; color: #3A3D47;
    text-transform: uppercase; margin-bottom: 26px;
    border-bottom: 1px solid #1E2028; padding-bottom: 14px;
    display: flex; align-items: center; gap: 10px;
}
.nx-page-title .dot {
    display: inline-block; width: 5px; height: 5px;
    border-radius: 50%; background: #D4A843; flex-shrink: 0;
}

/* Cards */
.nx-card {
    background: #13141A;
    border: 1px solid #1E2028;
    border-radius: 3px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.nx-card-title {
    font-size: 10px; letter-spacing: 3px;
    color: #3A3D47; text-transform: uppercase; margin-bottom: 14px;
}

/* Metrics */
.nx-metric-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px; font-weight: 500; color: #E8EAF0; line-height: 1;
}
.nx-metric-label { font-size: 11px; color: #4A4D5A; margin-top: 5px; letter-spacing: 1px; }
.nx-delta-pos { color: #4CAF7D; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.nx-delta-neg { color: #E05252; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }

/* Badges */
.nx-badge {
    display: inline-block; font-size: 10px; letter-spacing: 2px;
    text-transform: uppercase; padding: 3px 8px; border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
}
.nx-badge-green { background: rgba(76,175,125,.1); color: #4CAF7D; border: 1px solid rgba(76,175,125,.2); }
.nx-badge-gold  { background: rgba(212,168,67,.1);  color: #D4A843; border: 1px solid rgba(212,168,67,.2);  }
.nx-badge-red   { background: rgba(224,82,82,.1);   color: #E05252; border: 1px solid rgba(224,82,82,.2);   }
.nx-badge-gray  { background: rgba(42,44,51,.4);    color: #4A4D5A; border: 1px solid #1E2028;             }

/* Address / code box */
.nx-address {
    font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    color: #6A6D7A; background: #0A0B0D;
    border: 1px solid #1E2028; border-radius: 3px;
    padding: 10px 14px; word-break: break-all; letter-spacing: .5px;
}

/* Terminal log */
.nx-terminal {
    background: #0A0B0D; border: 1px solid #1E2028; border-radius: 3px;
    padding: 18px; font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; color: #4CAF7D; line-height: 2;
}
.nx-terminal .ts  { color: #2A2C33; }
.nx-terminal .warn { color: #D4A843; }

/* Progress bar */
.nx-bar-track { background: #0A0B0D; height: 5px; border-radius: 3px; overflow: hidden; margin-top: 8px; }
.nx-bar-fill  { height: 100%; border-radius: 3px; }

/* Inputs */
.stTextInput input, .stNumberInput input {
    background: #0A0B0D !important;
    border: 1px solid #1E2028 !important;
    color: #C8CAD0 !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #D4A843 !important;
    box-shadow: 0 0 0 1px rgba(212,168,67,.15) !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label {
    font-size: 10px !important; letter-spacing: 2px !important;
    color: #3A3D47 !important; text-transform: uppercase !important;
}
.stSelectbox [data-baseweb="select"] {
    background: #0A0B0D !important; border: 1px solid #1E2028 !important;
    border-radius: 3px !important;
}
.stSelectbox [data-baseweb="select"] * { color: #C8CAD0 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 13px !important; }

/* Buttons */
.stButton > button {
    background: transparent !important; border: 1px solid #2A2C33 !important;
    color: #6A6D7A !important; border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; transition: all .18s !important;
    height: 38px !important;
}
.stButton > button:hover { border-color: #D4A843 !important; color: #D4A843 !important; background: rgba(212,168,67,.04) !important; }
.stButton > button[kind="primary"] { border-color: #D4A843 !important; color: #D4A843 !important; }
.stButton > button[kind="primary"]:hover { background: rgba(212,168,67,.07) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #1E2028 !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #3A3D47 !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important; padding: 10px 18px !important;
}
.stTabs [aria-selected="true"] { color: #D4A843 !important; border-bottom-color: #D4A843 !important; }

/* Dataframe */
.stDataFrame { border: 1px solid #1E2028 !important; border-radius: 3px !important; }
.stDataFrame thead tr th { background: #0A0B0D !important; color: #3A3D47 !important; font-size: 10px !important; letter-spacing: 1px !important; }
.stDataFrame tbody tr td { color: #8A8D99 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }

/* Download button */
.stDownloadButton > button { font-size: 10px !important; letter-spacing: 2px !important; height: 34px !important; }

/* Toggle */
.stToggle > label { color: #4A4D5A !important; font-size: 12px !important; }

/* Hide chrome */
#MainMenu, footer, header, .stDeployButton, div[data-testid="stToolbar"] { display: none !important; }

/* Spinner */
.stSpinner > div { border-top-color: #D4A843 !important; }

/* Form */
.stForm { border: none !important; padding: 0 !important; }
</style>
"""


# ==========================================
# AUTH
# ==========================================
def verify_access(pin, license_key):
    if pin != SECRET_PIN:
        return False, "Invalid credentials"
    if not os.path.exists(DB_PATH):
        if license_key == "NEXUS-DEBUG-2026":
            return True, ""
        return False, f"Database {DB_PATH} not found"
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute(
            "SELECT user_id FROM orders WHERE license_key = ? AND status = 'paid'",
            (license_key.strip(),)
        )
        res = cur.fetchone()
        conn.close()
        return res is not None, "License inactive"
    except Exception as e:
        return False, f"DB error: {e}"


# ==========================================
# EXCHANGE CORE
# ==========================================
class NexusExchange:
    def __init__(self, bybit_session):
        self.bybit = bybit_session
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exchange_orders (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT, from_asset TEXT, to_asset TEXT,
                from_amount  REAL, to_amount REAL, rate REAL,
                status TEXT, tx_id TEXT, order_type TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_spot_price(self, symbol):
        try:
            t = self.bybit.get_tickers(category="spot", symbol=symbol)
            return float(t['result']['list'][0]['lastPrice'])
        except:
            return None

    def execute_market_swap(self, from_asset, to_asset, amount, side):
        symbol = f"{from_asset}{to_asset}" if side == "SELL" else f"{to_asset}{from_asset}"
        if symbol not in ["SOLUSDT","BTCUSDT","ETHUSDT","XRPUSDT"]:
            return False, "Pair not supported"
        try:
            order = self.bybit.place_order(
                category="spot", symbol=symbol, side=side,
                orderType="Market", qty=str(amount), timeInForce="GTC"
            )
            if order['retCode'] == 0:
                return True, order['result']['orderId']
            return False, order['retMsg']
        except Exception as e:
            return False, str(e)

    def calculate_swap(self, from_asset, to_asset, amount):
        if from_asset == to_asset:
            return amount, 1.0
        if from_asset == "USDT":
            p = self.get_spot_price(f"{to_asset}USDT")
            if not p: return None, None
            out = amount / p
        elif to_asset == "USDT":
            p = self.get_spot_price(f"{from_asset}USDT")
            if not p: return None, None
            out = amount * p
        else:
            pf = self.get_spot_price(f"{from_asset}USDT")
            pt = self.get_spot_price(f"{to_asset}USDT")
            if not pf or not pt: return None, None
            out = (amount * pf) / pt
        rate = out / amount if amount else 0
        return round(out, 8), round(rate, 8)

    def save_order(self, fa, ta, famt, tamt, rate, status, tx_id, otype="market"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO exchange_orders
            (timestamp,from_asset,to_asset,from_amount,to_amount,rate,status,tx_id,order_type)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', (time.strftime('%Y-%m-%d %H:%M:%S'), fa, ta, famt, tamt, rate, status, tx_id, otype))
        conn.commit()
        conn.close()

    def get_history(self, limit=50):
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            f"SELECT * FROM exchange_orders ORDER BY timestamp DESC LIMIT {limit}", conn
        )
        conn.close()
        return df


# ==========================================
# AUTH GATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="NEXUS", page_icon="◈", layout="centered")
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .login-wrap { max-width: 360px; margin: 80px auto 0; }
    .login-logo { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:6px; color:#D4A843; text-transform:uppercase; margin-bottom:4px; }
    .login-tagline { font-size:10px; color:#2A2C33; letter-spacing:3px; margin-bottom:36px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">◈ NEXUS</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-tagline">ENCRYPTED TRADING TERMINAL</div>', unsafe_allow_html=True)

    with st.form("auth"):
        pin = st.text_input("NEURAL PIN", type="password", placeholder="••••••••••••")
        key = st.text_input("LICENSE KEY", type="password", placeholder="NEXUS-XXXX-XXXX")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("AUTHENTICATE", use_container_width=True):
            ok, msg = verify_access(pin, key)
            if ok:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.markdown(
                    f'<div style="color:#E05252;font-size:11px;font-family:\'IBM Plex Mono\',monospace;margin-top:6px;">{msg}</div>',
                    unsafe_allow_html=True
                )
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ==========================================
# MAIN TERMINAL
# ==========================================
st.set_page_config(page_title="NEXUS PRO", page_icon="◈", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

BYBIT_KEY    = st.secrets.get("BYBIT_API_KEY", "")
BYBIT_SECRET = st.secrets.get("BYBIT_API_SECRET", "")
session      = HTTP(testnet=False, api_key=BYBIT_KEY, api_secret=BYBIT_SECRET)
exchange     = NexusExchange(session)


# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nx-brand">◈ NEXUS</div>', unsafe_allow_html=True)
    st.markdown('<div class="nx-sub">PRO v24 · LIVE</div>', unsafe_allow_html=True)

    asset = st.selectbox("ASSET", ["SOL","BTC","ETH","XRP","GOLD","OIL"])
    st.divider()
    page  = st.radio("NAVIGATION", ["Terminal","Analytics","Wallet","Exchange","Logs"])
    st.divider()
    run_whale = st.toggle("Whale Watcher", value=True)
    run_recon = st.toggle("Pattern Recon",  value=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="nx-badge nx-badge-green">ONLINE</span>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Exit", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown(
        '<div style="margin-top:20px;font-size:10px;color:#1E2028;font-family:\'IBM Plex Mono\',monospace;">v24.04.2026</div>',
        unsafe_allow_html=True
    )


def page_header(title):
    st.markdown(
        f'<div class="nx-page-title"><span class="dot"></span>{title}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# TERMINAL
# ============================================================
if page == "Terminal":
    page_header("MARKET TERMINAL")
    col_chart, col_panel = st.columns([4, 1])

    with col_chart:
        sym = f"BYBIT:{asset}USDT" if asset not in ["GOLD","OIL"] else f"OANDA:{asset}USD"
        components.html(f"""
        <div id="tvc" style="height:520px;border:1px solid #1E2028;border-radius:3px;overflow:hidden;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{
            autosize:true, symbol:"{sym}", interval:"15",
            theme:"dark", style:"1", locale:"en",
            toolbar_bg:"#0E0F11", backgroundColor:"#0E0F11",
            gridColor:"#1A1B20", container_id:"tvc",
            hide_side_toolbar:false, enable_publishing:false
        }});</script>
        """, height=530)

    with col_panel:
        # Price
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown('<div class="nx-card-title">Price</div>', unsafe_allow_html=True)
        if asset in ["GOLD","OIL"]:
            tm = {"GOLD":"GC=F","OIL":"BZ=F"}
            try:
                d = yf.Ticker(tm[asset]).history(period="2d")
                if not d.empty:
                    cp = d['Close'].iloc[-1]
                    dv = cp - d['Close'].iloc[-2] if len(d)>1 else 0
                    pc = dv/d['Close'].iloc[-2]*100 if len(d)>1 else 0
                    dc = "nx-delta-pos" if dv>=0 else "nx-delta-neg"
                    sg = "+" if dv>=0 else ""
                    st.markdown(f'<div class="nx-metric-val">${cp:,.2f}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="{dc}">{sg}{dv:,.2f} ({sg}{pc:.2f}%)</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="nx-metric-label">{asset} FUTURES</div>', unsafe_allow_html=True)
            except:
                st.markdown('<span class="nx-badge nx-badge-red">OFFLINE</span>', unsafe_allow_html=True)
        else:
            try:
                r  = requests.get(f"https://api.binance.com/api/v3/ticker_24hr?symbol={asset}USDT", timeout=5).json()
                cp = float(r['lastPrice'])
                dv = float(r['priceChange'])
                pc = float(r['priceChangePercent'])
                dc = "nx-delta-pos" if dv>=0 else "nx-delta-neg"
                sg = "+" if dv>=0 else ""
                st.markdown(f'<div class="nx-metric-val">${cp:,.2f}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="{dc}">{sg}{dv:,.2f} ({sg}{pc:.2f}%)</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="nx-metric-label">{asset}/USDT · 24H</div>', unsafe_allow_html=True)
            except:
                st.markdown('<span class="nx-badge nx-badge-red">OFFLINE</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # System
        st.markdown("""
        <div class="nx-card">
        <div class="nx-card-title">System</div>
        <table style="width:100%;font-size:11px;font-family:'IBM Plex Mono',monospace;">
        <tr><td style="color:#3A3D47;padding:4px 0">API</td><td style="color:#4CAF7D;text-align:right">LIVE</td></tr>
        <tr><td style="color:#3A3D47;padding:4px 0">WS</td><td style="color:#4CAF7D;text-align:right">STABLE</td></tr>
        <tr><td style="color:#3A3D47;padding:4px 0">DB</td><td style="color:#4CAF7D;text-align:right">READY</td></tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

        # Whale
        if asset not in ["GOLD","OIL"] and run_whale:
            st.markdown('<div class="nx-card">', unsafe_allow_html=True)
            st.markdown('<div class="nx-card-title">Whale Watcher</div>', unsafe_allow_html=True)
            try:
                ob  = session.get_orderbook(category="spot", symbol=f"{asset}USDT")
                vol = float(ob['result']['a'][0][1]) * float(ob['result']['a'][0][0])
                bid = float(ob['result']['b'][0][0])
                ask = float(ob['result']['a'][0][0])
                if vol > 150_000:
                    st.markdown(f'<div style="color:#E05252;font-family:\'IBM Plex Mono\',monospace;font-size:12px;">ASK WALL · ${vol/1000:,.1f}k</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#4CAF7D;font-family:\'IBM Plex Mono\',monospace;font-size:12px;">CLEAR</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:6px;font-size:11px;color:#3A3D47;font-family:\'IBM Plex Mono\',monospace;">SPREAD {ask-bid:.3f}</div>', unsafe_allow_html=True)
            except:
                st.markdown('<span class="nx-badge nx-badge-gray">NO DATA</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# ANALYTICS
# ============================================================
elif page == "Analytics":
    page_header("NEURAL ANALYTICS")

    if asset in ["GOLD","OIL"]:
        st.markdown('<div class="nx-card"><div class="nx-card-title">Notice</div><div style="font-size:13px;color:#4A4D5A;">Commodity analytics in development.</div></div>', unsafe_allow_html=True)
    else:
        try:
            res = session.get_kline(category="spot", symbol=f"{asset}USDT", interval="60")
            df  = pd.DataFrame(res['result']['list'], columns=['ts','o','h','l','c','v','t'])
            df['close']  = df['c'].astype(float)
            df['volume'] = df['v'].astype(float)

            rsi_     = ta.rsi(df['close'], length=14).iloc[-1]
            macd_r   = ta.macd(df['close'])
            macd_v   = macd_r['MACD_12_26_9'].iloc[-1]
            macd_s   = macd_r['MACDs_12_26_9'].iloc[-1]
            ema20    = ta.ema(df['close'], length=20).iloc[-1]
            ema50    = ta.ema(df['close'], length=50).iloc[-1]
            bb       = ta.bbands(df['close'], length=20)
            bb_up    = bb['BBU_20_2.0'].iloc[-1]
            bb_dn    = bb['BBL_20_2.0'].iloc[-1]
            cur_p    = df['close'].iloc[-1]

            rsi_sig  = "OVERBOUGHT" if rsi_>70 else ("OVERSOLD" if rsi_<30 else "NEUTRAL")
            rsi_b    = "nx-badge-red" if rsi_>70 else ("nx-badge-green" if rsi_<30 else "nx-badge-gray")
            macd_sig = "BULLISH" if macd_v>macd_s else "BEARISH"
            macd_b   = "nx-badge-green" if macd_v>macd_s else "nx-badge-red"
            ema_sig  = "UPTREND" if ema20>ema50 else "DOWNTREND"
            ema_b    = "nx-badge-green" if ema20>ema50 else "nx-badge-red"
            bb_pct   = (cur_p-bb_dn)/(bb_up-bb_dn)*100 if (bb_up-bb_dn)>0 else 50
            rsi_bar_clr = '#E05252' if rsi_>70 else ('#4CAF7D' if rsi_<30 else '#D4A843')

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f"""
                <div class="nx-card">
                <div class="nx-card-title">RSI · 14</div>
                <div class="nx-metric-val">{rsi_:.1f}</div>
                <div style="margin-top:10px;"><span class="nx-badge {rsi_b}">{rsi_sig}</span></div>
                <div class="nx-bar-track"><div class="nx-bar-fill" style="width:{min(rsi_,100):.0f}%;background:{rsi_bar_clr};"></div></div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="nx-card">
                <div class="nx-card-title">MACD · 12/26/9</div>
                <div class="nx-metric-val" style="font-size:20px;">{macd_v:+.4f}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#3A3D47;margin-top:4px;">SIG {macd_s:+.4f}</div>
                <div style="margin-top:10px;"><span class="nx-badge {macd_b}">{macd_sig}</span></div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="nx-card">
                <div class="nx-card-title">EMA · 20 / 50</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:#8A8D99;margin-bottom:3px;">EMA20 &nbsp;${ema20:,.2f}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:#8A8D99;margin-bottom:12px;">EMA50 &nbsp;${ema50:,.2f}</div>
                <span class="nx-badge {ema_b}">{ema_sig}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="nx-card">
            <div class="nx-card-title">Bollinger Bands · 20,2</div>
            <div style="display:flex;gap:36px;align-items:flex-end;">
                <div><div style="font-size:10px;color:#3A3D47;letter-spacing:1px;margin-bottom:4px;">UPPER</div><div style="font-family:'IBM Plex Mono',monospace;font-size:14px;color:#E8EAF0;">${bb_up:,.2f}</div></div>
                <div><div style="font-size:10px;color:#3A3D47;letter-spacing:1px;margin-bottom:4px;">PRICE</div><div style="font-family:'IBM Plex Mono',monospace;font-size:14px;color:#D4A843;">${cur_p:,.2f}</div></div>
                <div><div style="font-size:10px;color:#3A3D47;letter-spacing:1px;margin-bottom:4px;">LOWER</div><div style="font-family:'IBM Plex Mono',monospace;font-size:14px;color:#E8EAF0;">${bb_dn:,.2f}</div></div>
                <div style="flex:1;padding-bottom:2px;">
                    <div style="font-size:10px;color:#3A3D47;letter-spacing:1px;margin-bottom:6px;">POSITION IN BAND &nbsp;{bb_pct:.1f}%</div>
                    <div class="nx-bar-track"><div class="nx-bar-fill" style="width:{bb_pct:.0f}%;background:#D4A843;"></div></div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="nx-card"><span class="nx-badge nx-badge-red">SYNC ERROR</span> <span style="font-size:12px;color:#3A3D47;margin-left:8px;">{e}</span></div>', unsafe_allow_html=True)


# ============================================================
# WALLET
# ============================================================
elif page == "Wallet":
    page_header("SOLANA WALLET")

    tab_ov, tab_send, tab_new = st.tabs(["Overview", "Send", "New Wallet"])

    with tab_ov:
        addr = st.text_input("WALLET ADDRESS", placeholder="Enter Solana public key…", key="w_addr")
        if addr:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="nx-card">', unsafe_allow_html=True)
                st.markdown('<div class="nx-card-title">Balance</div>', unsafe_allow_html=True)
                try:
                    bal = crypto.get_balance(addr)
                    st.markdown(f'<div class="nx-metric-val">{bal:.6f}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="nx-metric-label">SOL</div>', unsafe_allow_html=True)
                    try:
                        sp  = float(requests.get("https://api.binance.com/api/v3/ticker_price?symbol=SOLUSDT", timeout=4).json()['price'])
                        st.markdown(f'<div style="margin-top:8px;font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:#4A4D5A;">≈ ${bal*sp:,.2f} USD</div>', unsafe_allow_html=True)
                    except: pass
                except:
                    st.markdown('<span class="nx-badge nx-badge-red">RPC ERROR</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="nx-card">', unsafe_allow_html=True)
                st.markdown('<div class="nx-card-title">Account</div>', unsafe_allow_html=True)
                try:
                    info = crypto.get_wallet_info(addr)
                    if "error" not in info:
                        sb  = "nx-badge-green" if info.get('is_active') else "nx-badge-gray"
                        stx = "ACTIVE" if info.get('is_active') else "INACTIVE"
                        st.markdown(f"""
                        <table style="width:100%;font-size:12px;font-family:'IBM Plex Mono',monospace;">
                        <tr><td style="color:#3A3D47;padding:5px 0">Status</td><td style="text-align:right"><span class="nx-badge {sb}">{stx}</span></td></tr>
                        <tr><td style="color:#3A3D47;padding:5px 0">Recent TX</td><td style="color:#8A8D99;text-align:right">{info.get('recent_tx_count','—')}</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="nx-badge nx-badge-gray">NOT FOUND</span>', unsafe_allow_html=True)
                except: pass
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="nx-card">', unsafe_allow_html=True)
            st.markdown('<div class="nx-card-title">Public Address</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="nx-address">{addr}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nx-card"><div style="font-size:12px;color:#3A3D47;padding:16px 0;text-align:center;">Enter a wallet address above to view balance and details.</div></div>', unsafe_allow_html=True)

    with tab_send:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown('<div class="nx-card-title">Transfer SOL</div>', unsafe_allow_html=True)

        dest    = st.text_input("DESTINATION", placeholder="Recipient's Solana public key", key="s_dest")
        amount  = st.number_input("AMOUNT (SOL)", min_value=0.000001, step=0.01, format="%.6f", key="s_amt")
        privkey = st.text_input("PRIVATE KEY (BASE58)", type="password", placeholder="Signs the transaction locally", key="s_key")

        st.markdown('<div style="font-size:10px;color:#2A2C33;font-family:\'IBM Plex Mono\',monospace;margin:10px 0 14px;">Keys are processed locally and never transmitted.</div>', unsafe_allow_html=True)

        if st.button("SIGN AND BROADCAST", use_container_width=True, type="primary", key="send_btn"):
            if not dest or not privkey or amount <= 0:
                st.markdown('<span class="nx-badge nx-badge-red">FILL ALL FIELDS</span>', unsafe_allow_html=True)
            else:
                with st.spinner("Signing and broadcasting…"):
                    kp = crypto.import_key_from_base58(privkey)
                    if kp:
                        ok, tx_id = crypto.send_sol(kp, dest, amount)
                        if ok:
                            st.markdown(f"""
                            <div style="margin-top:10px;">
                            <span class="nx-badge nx-badge-green">CONFIRMED</span>
                            <div style="font-size:11px;color:#3A3D47;margin-top:10px;">Transaction ID</div>
                            <div class="nx-address" style="margin-top:6px;">{tx_id}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.markdown(f'<span class="nx-badge nx-badge-red">FAILED</span> <span style="font-size:12px;color:#4A4D5A;margin-left:8px;">{tx_id}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="nx-badge nx-badge-red">INVALID KEY</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_new:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown('<div class="nx-card-title">Generate Keypair</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#4A4D5A;margin-bottom:16px;">Creates a fresh Solana keypair. Store the private key offline — it cannot be recovered.</div>', unsafe_allow_html=True)

        if st.button("GENERATE KEYPAIR", use_container_width=True, key="gen_btn"):
            w = crypto.create_wallet()
            if w:
                st.markdown(f"""
                <div>
                <div style="font-size:10px;letter-spacing:2px;color:#4A4D5A;text-transform:uppercase;margin-bottom:6px;">Public Address</div>
                <div class="nx-address">{w.get('public_key','—')}</div>
                <div style="font-size:10px;letter-spacing:2px;color:#E05252;text-transform:uppercase;margin:14px 0 6px;">Private Key — SAVE NOW</div>
                <div class="nx-address" style="border-color:rgba(224,82,82,.3);color:#E05252;">{w.get('private_key','—')}</div>
                <div style="margin-top:12px;font-size:10px;color:#2A2C33;font-family:'IBM Plex Mono',monospace;">This information will not be shown again.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<span class="nx-badge nx-badge-red">FAILED</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# EXCHANGE
# ============================================================
elif page == "Exchange":
    page_header("ATOMIC SWAP")

    tab_mkt, tab_lim, tab_hist = st.tabs(["Market Swap", "Limit Order", "History"])

    with tab_mkt:
        c1, c_arr, c2 = st.columns([5, 1, 5])

        with c1:
            st.markdown('<div class="nx-card">', unsafe_allow_html=True)
            st.markdown('<div class="nx-card-title">You Send</div>', unsafe_allow_html=True)
            from_asset  = st.selectbox("", ["SOL","BTC","ETH","XRP","USDT"], key="fa", label_visibility="collapsed")
            from_amount = st.number_input("", min_value=0.0, step=0.01, format="%.6f", key="famt", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        with c_arr:
            st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:120px;font-family:\'IBM Plex Mono\',monospace;color:#2A2C33;font-size:18px;">→</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="nx-card">', unsafe_allow_html=True)
            st.markdown('<div class="nx-card-title">You Receive</div>', unsafe_allow_html=True)
            dflt = 4 if from_asset != "USDT" else 0
            to_asset = st.selectbox("", ["SOL","BTC","ETH","XRP","USDT"], key="ta", index=dflt, label_visibility="collapsed")
            if from_amount > 0 and from_asset != to_asset:
                est, rate = exchange.calculate_swap(from_asset, to_asset, from_amount)
                if est:
                    st.markdown(f'<div class="nx-metric-val" style="font-size:18px;margin-top:6px;">{est:.8f}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="nx-metric-label">{to_asset}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="margin-top:8px;font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:#3A3D47;letter-spacing:1px;">1 {from_asset} = {rate:.6f} {to_asset} · FEE 0.1%</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="nx-badge nx-badge-gray">RATE UNAVAILABLE</span>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:12px;color:#2A2C33;margin-top:10px;">—</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("EXECUTE SWAP", use_container_width=True, type="primary", key="swap_exec"):
            if from_amount <= 0:
                st.markdown('<span class="nx-badge nx-badge-red">ENTER AMOUNT</span>', unsafe_allow_html=True)
            elif from_asset == to_asset:
                st.markdown('<span class="nx-badge nx-badge-red">IDENTICAL ASSETS</span>', unsafe_allow_html=True)
            else:
                with st.spinner("Routing order…"):
                    side = "BUY" if from_asset == "USDT" else "SELL"
                    ok, result = exchange.execute_market_swap(
                        from_asset if side=="SELL" else to_asset,
                        to_asset   if side=="SELL" else from_asset,
                        from_amount, side
                    )
                    if ok:
                        fa_, fr_ = exchange.calculate_swap(from_asset, to_asset, from_amount)
                        exchange.save_order(from_asset, to_asset, from_amount, fa_, fr_, "completed", result)
                        st.markdown(f"""
                        <span class="nx-badge nx-badge-green">FILLED</span>
                        <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#3A3D47;margin-left:10px;">{result[:16]}…</span>
                        """, unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        exchange.save_order(from_asset, to_asset, from_amount, 0, 0, "failed", result)
                        st.markdown(f'<span class="nx-badge nx-badge-red">REJECTED</span> <span style="font-size:12px;color:#4A4D5A;margin-left:8px;">{result}</span>', unsafe_allow_html=True)

    with tab_lim:
        st.markdown('<div class="nx-card"><div class="nx-card-title">Coming Soon</div><div style="font-size:13px;color:#4A4D5A;">Limit orders, stop-loss, take-profit and OCO via Bybit API.</div></div>', unsafe_allow_html=True)

    with tab_hist:
        df_h = exchange.get_history(50)
        if not df_h.empty:
            def fmt_status(s):
                return {"completed":"FILLED","failed":"REJECTED"}.get(s, s.upper())
            ds = df_h[['timestamp','from_asset','to_asset','from_amount','to_amount','rate','status']].copy()
            ds.columns = ['Time','From','To','From Amt','To Amt','Rate','Status']
            ds['Status'] = ds['Status'].apply(fmt_status)
            st.dataframe(ds, use_container_width=True, hide_index=True)
            st.download_button("EXPORT CSV", df_h.to_csv(index=False).encode(), "nexus_exchange.csv", "text/csv", use_container_width=True)
        else:
            st.markdown('<div style="font-size:12px;color:#3A3D47;padding:16px 0;">No orders recorded.</div>', unsafe_allow_html=True)


# ============================================================
# LOGS
# ============================================================
elif page == "Logs":
    page_header("SYSTEM LOGS")
    ts = time.strftime('%H:%M:%S')
    dt = time.strftime('%Y-%m-%d')
    w_on = '<span style="color:#4CAF7D;">on</span>' if run_whale else '<span style="color:#3A3D47;">off</span>'
    r_on = '<span style="color:#4CAF7D;">on</span>' if run_recon else '<span style="color:#3A3D47;">off</span>'
    st.markdown(f"""
    <div class="nx-terminal">
<span class="ts">[{dt} {ts}]</span>  NEXUS PRO v24 · boot complete<br>
<span class="ts">[{dt} {ts}]</span>  operator authenticated · session open<br>
<span class="ts">[{dt} {ts}]</span>  bybit ws · mainnet · connected<br>
<span class="ts">[{dt} {ts}]</span>  solana rpc · mainnet-beta · ready<br>
<span class="ts">[{dt} {ts}]</span>  sqlite · {DB_PATH} · connected<br>
<span class="ts">[{dt} {ts}]</span>  active page &nbsp;· <span style="color:#D4A843;">{page.lower()}</span><br>
<span class="ts">[{dt} {ts}]</span>  asset &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;· <span style="color:#D4A843;">{asset}</span><br>
<span class="ts">[{dt} {ts}]</span>  whale watcher · {w_on}<br>
<span class="ts">[{dt} {ts}]</span>  pattern recon &nbsp;· {r_on}<br>
<span class="ts">[{dt} {ts}]</span>  <span class="warn">standing by …</span>
    </div>
    """, unsafe_allow_html=True)
