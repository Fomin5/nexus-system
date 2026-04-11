import streamlit as st
import qrcode
from io import BytesIO
import streamlit.components.v1 as components
import requests
import time

# --- 1. LIVE DATA ENGINE ---
@st.cache_data(ttl=15)
def get_sol_price():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT", timeout=2)
        return float(res.json()['price'])
    except:
        return 145.20

# --- 2. LAYOUT CONFIG ---
st.set_page_config(page_title="NEXUS AI TERMINAL", layout="wide", initial_sidebar_state="expanded")
current_sol_price = get_sol_price()

# --- 3. ADAPTIVE STYLES (CSS) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #050505; color: white; }}
    
    /* ADAPTIVE PHANTOM WINDOW */
    .phantom-window {{
        position: fixed; 
        top: 60px; 
        right: 20px; 
        width: 340px; 
        max-width: 90vw; 
        max-height: 80vh;
        background-color: rgba(26, 26, 26, 0.98); 
        border: 1px solid #333; 
        border-radius: 24px;
        z-index: 1000; 
        box-shadow: 0 20px 60px rgba(0,0,0,1);
        padding: 18px; 
        display: flex; 
        flex-direction: column;
        overflow-y: auto;
        animation: fadeIn 0.3s ease-out;
    }}
    
    @media (max-width: 480px) {{
        .phantom-window {{ right: 5vw; left: 5vw; width: 90vw; top: 50px; }}
    }}

    .wallet-header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
    .asset-row {{ 
        display: flex; justify-content: space-between; padding: 12px; 
        background: #222; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333;
    }}
    
    div.stButton > button {{ border-radius: 10px; font-weight: 600; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. STATE MANAGEMENT ---
if "phantom_visible" not in st.session_state: st.session_state.phantom_visible = False
if "connected" not in st.session_state: st.session_state.connected = False

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("⚡ NEXUS CORE")
    if not st.session_state.connected:
        if st.button("👻 Connect Phantom", use_container_width=True):
            st.session_state.connected = True
            st.rerun()
    else:
        label = f"👛 BjwVt...XqhU7J | ${current_sol_price:.2f}"
        if st.button(label, use_container_width=True):
            st.session_state.phantom_visible = not st.session_state.phantom_visible
            st.rerun()
    
    st.divider()
    page = st.radio("MENU", ["📈 Terminal", "💎 License"])

# --- 6. PHANTOM OVERLAY ---
if st.session_state.connected and st.session_state.phantom_visible:
    sol_amt = 12.55
    total_usd = (sol_amt * current_sol_price) + 105.00
    
    st.markdown('<div class="phantom-window">', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="wallet-header">
            <span style="color:#ab9ff2; font-weight:bold;">Phantom</span>
            <span style="font-size:10px; background:#333; padding:2px 8px; border-radius:10px;">Mainnet</span>
        </div>
        <div style="text-align:center; margin-bottom:15px;">
            <p style="color:#888; font-size:12px; margin:0;">Balance</p>
            <h2 style="margin:0; font-size:32px;">${total_usd:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.link_button("📥 Deposit", "https://www.bybit.com/fiat/trade/otc/?coin=SOL&fiat=RUB", use_container_width=True)
    with c2:
        if st.button("📤 Send", use_container_width=True):
            st.toast("Redirecting to License for payment...")
            time.sleep(1)
    
    st.markdown(f"""
        <div style="margin-top:15px;"></div>
        <div class="asset-row"><span>Solana</span><b>{sol_amt} SOL</b></div>
        <div class="asset-row"><span>USDC</span><b>$105.00</b></div>
    """, unsafe_allow_html=True)

    if st.button("❌ Close", use_container_width=True):
        st.session_state.phantom_visible = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. PAGES ---
if page == "📈 Terminal":
    st.title(f"SOL/USDT Live — ${current_sol_price}")
    components.html(f"""
        <div style="height:600px; border:1px solid #333; border-radius:16px; overflow:hidden;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>new TradingView.widget({{"autosize":true,"symbol":"BYBIT:SOLUSDT","interval":"1","theme":"dark","container_id":"tv_chart","locale":"en"}});</script>
        </div>
    """, height=610)

elif page == "💎 License":
    st.header("💎 Nexus Pro License")
    st.divider()
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.write("### AI Signals Activation")
        u_name = st.text_input("Username (TG/Discord):")
    with col_r:
        st.markdown('<div style="background:#111; padding:20px; border-radius:15px; border:1px solid #ab9ff2; text-align:center;"><h4>Price: 0.5 SOL</h4></div>', unsafe_allow_html=True)
        if st.button("ACTIVATE NOW", use_container_width=True):
            if u_name:
                pay_url = f"solana:BjwVtUF8t74k1WJ5jxN51gnhyekYvzs89u6whoXqhU7J?amount=0.5&memo=PRO:{u_name}"
                qr = qrcode.make(pay_url)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf.getvalue(), caption="Scan to Pay", width=250)
            else: st.warning("Enter your username!")
