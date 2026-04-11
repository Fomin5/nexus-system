import streamlit as st
import requests
import streamlit.components.v1 as components
from pybit.unified_trading import HTTP
import time

# --- 1. CONFIG & SECRETS ---
st.set_page_config(page_title="NEXUS ULTIMATE", layout="wide")

# Correct Secret Handling: These look for variables in Streamlit Cloud Settings
BYBIT_KEY = st.secrets.get("BYBIT_API_KEY", "")
BYBIT_SECRET = st.secrets.get("BYBIT_API_SECRET", "")

@st.cache_data(ttl=15)
def get_sol_price():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker_price?symbol=SOLUSDT", timeout=2)
        return float(res.json()['price'])
    except:
        return 150.0

def get_real_balance(api_key, api_secret):
    """Fetches real SOL balance from Bybit Unified Account"""
    if not api_key or not api_secret:
        return 0.0
    try:
        session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)
        result = session.get_wallet_balance(accountType="UNIFIED", coin="SOL")
        balance = result['result']['list'][0]['coin'][0]['walletBalance']
        return float(balance)
    except:
        return 0.0

def test_bybit_connection(api_key, api_secret):
    """API Connection Test with Server Time Sync"""
    try:
        temp_session = HTTP(testnet=False)
        server_time = temp_session.get_server_time()['result']['timeSecond']
        
        session = HTTP(
            testnet=False, 
            api_key=api_key, 
            api_secret=api_secret,
            recv_window=20000 
        )
        session.get_wallet_balance(accountType="UNIFIED", coin="SOL")
        return True, "Connection Successful"
    except Exception as e:
        return False, str(e)

# --- 2. STYLES ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .phantom-window {
        position: fixed; top: 80px; right: 20px; width: 340px; 
        background-color: rgba(20, 20, 20, 0.98); border: 1px solid #333; 
        border-radius: 20px; z-index: 1000; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .asset-row { display: flex; justify-content: space-between; padding: 10px; background: #111; border-radius: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE ---
if "connected" not in st.session_state: st.session_state.connected = False
if "wallet_open" not in st.session_state: st.session_state.wallet_open = False
current_sol_price = get_sol_price()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚡ NEXUS CORE")
    if not st.session_state.connected:
        if st.button("👻 Connect Wallet", use_container_width=True, type="primary"):
            st.session_state.connected = True
            st.rerun()
    else:
        # Use Secrets for balance display in sidebar
        display_bal = get_real_balance(BYBIT_KEY, BYBIT_SECRET)
        if st.button(f"👛 Wallet: ${display_bal * current_sol_price:,.2f}", use_container_width=True):
            st.session_state.wallet_open = not st.session_state.wallet_open
            st.rerun()
    
    st.divider()
    page = st.radio("MODULES", ["📈 Terminal", "🛠 Tunnel Settings"])

# --- 5. WALLET OVERLAY ---
if st.session_state.connected and st.session_state.wallet_open:
    sol_bal = get_real_balance(BYBIT_KEY, BYBIT_SECRET)
    kgs_rate = 90.5 # Estimated P2P rate for MBank
    
    st.markdown('<div class="phantom-window">', unsafe_allow_html=True)
    st.markdown(f"### Total: ${sol_bal * current_sol_price:,.2f}")
    st.markdown(f"**Est. Cashout: {(sol_bal * current_sol_price) * kgs_rate:,.2f} KGS**")
    
    c1, c2 = st.columns(2)
    with c1: st.link_button("📥 Buy", "https://www.bybit.com/fiat/trade/otc/?coin=USDT&fiat=KGS", use_container_width=True)
    with c2: 
        if st.button("🏛 Withdraw", use_container_width=True):
            st.toast("Initiating Bybit -> MBank Tunnel...")
            
    st.markdown(f'<div class="asset-row"><span>Solana</span><b>{sol_bal:.4f} SOL</b></div>', unsafe_allow_html=True)
    if st.button("❌ Close", use_container_width=True):
        st.session_state.wallet_open = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. PAGES ---
if page == "📈 Terminal":
    st.subheader(f"SOL/USDT Live — ${current_sol_price}")
    components.html(f"""
        <div style="height:600px; border:1px solid #333; border-radius:15px; overflow:hidden;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
                new TradingView.widget({{"autosize": true, "symbol": "BYBIT:SOLUSDT", "interval": "1", "theme": "dark", "container_id": "tv_chart"}});
            </script>
        </div>
    """, height=610)

elif page == "🛠 Tunnel Settings":
    st.header("Tunnel Configuration")
    
    # Input fields use values from Secrets if available
    key_in = st.text_input("Bybit API Key", value=BYBIT_KEY, type="password")
    sec_in = st.text_input("Bybit API Secret", value=BYBIT_SECRET, type="password")
    phone = st.text_input("MBank Phone Number", placeholder="+996...")
    
    if st.button("Save & Test Connection"):
        if key_in and sec_in:
            with st.spinner("Testing bridge..."):
                success, msg = test_bybit_connection(key_in, sec_in)
                if success:
                    st.success(f"✅ {msg}! Tunnel operational.")
                    st.balloons()
                else: 
                    st.error(f"❌ Error: {msg}")
        else:
            st.warning("Please enter API keys.")
