import streamlit as st
import qrcode
from io import BytesIO

# --- PROFESSIONAL TRADER CONFIG ---
st.set_page_config(page_title="NEXUS TRADER HUB", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    .stButton>button { 
        background-color: #00E676; 
        color: black; 
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00C853; transform: scale(1.02); }
    .stTextInput>div>div>input {
        background-color: #111;
        color: #00E676;
        border: 1px solid #333;
        text-align: center;
    }
    .status-box {
        padding: 5px 15px; border-radius: 20px; border: 1px solid #00E676;
        background-color: rgba(0, 230, 118, 0.1); color: #00E676; font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP BAR ---
col_logo, col_stat = st.columns([3, 1])
with col_logo:
    st.title("⚡ NEXUS SYSTEM")
    st.caption("Advanced Infrastructure for Professional Traders")
with col_stat:
    st.markdown('<div class="status-box">● TRADING MODE ACTIVE</div>', unsafe_allow_html=True)

st.divider()

# --- SETUP WALLETS ---
st.subheader("🚀 Infrastructure Setup")
ob_c1, ob_c2, ob_c3 = st.columns(3)
with ob_c1: st.link_button("📈 Bybit Terminal", "https://www.bybit.com/trade/spot/EDGE/USDT", use_container_width=True)
with ob_c2: st.link_button("👻 Phantom Wall", "https://phantom.app/", use_container_width=True)
with ob_c3: st.link_button("🦊 MetaMask", "https://metamask.io/", use_container_width=True)

st.divider()

# --- LICENSE SECTION ---
st.subheader("💎 License Activation")
auth_method = st.radio("Identity Provider:", ["Telegram", "Discord", "X (Twitter)"], horizontal=True)
user_input = st.text_input("Enter Username:", placeholder="e.g. yarik_trader")
asset = st.selectbox("Funding Asset:", ["Solana (SOL)", "Bitcoin (BTC)", "Ethereum (ETH)"])

assets_data = {
    "Solana (SOL)": {"addr": "BjwVtUF8t74k1WJ5jxN51gnhyekYvzs89u6whoXqhU7J", "price": 0.5, "prefix": "solana:"},
    "Bitcoin (BTC)": {"addr": "YOUR_BTC_ADDR", "price": 0.00015, "prefix": "bitcoin:"},
    "Ethereum (ETH)": {"addr": "YOUR_ETH_ADDR", "price": 0.003, "prefix": "ethereum:"}
}

if st.button("PROCEED TO CHECKOUT"):
    if not user_input:
        st.warning("Identification required!")
    else:
        selected = assets_data[asset]
        memo = f"{auth_method[0]}:{user_input.strip()}"
        pay_url = f"{selected['prefix']}{selected['addr']}?amount={selected['price']}&memo={memo}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(pay_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf)
        
        st.divider()
        q_col, t_col = st.columns([1, 1])
        with q_col:
            st.image(buf.getvalue(), width=280)
        with t_col:
            st.success("Invoice Generated")
            st.write(f"**Network:** {asset}")
            st.write(f"**Amount:** {selected['price']}")
            st.info(f"Identity: {memo}")
            st.caption("License will be activated after 1 confirmation.")

st.container(height=50)

# --- FOOTER ---
st.divider()
st.write("### 🌐 Connect with Community:")
f1, f2, f3, f4 = st.columns(4)
with f1: st.link_button("✈️ Pay Bot", "https://t.me/...")
with f2: st.link_button("📢 Channel", "https://t.me/...")
with f3: st.link_button("👥 Discord", "https://discord.gg/...")
with f4: st.link_button("🐦 Twitter", "https://x.com/...")

st.caption("Nexus Core v4.5 | Global Multi-Asset Deployment")