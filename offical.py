import streamlit as st
import streamlit.components.v1 as components

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="NEXUS PRO | Official", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    /* Главный фон и шрифт */
    .stApp { background-color: #050505; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Неоновые карточки */
    .feature-card {
        padding: 25px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #333;
        transition: 0.3s;
        text-align: center;
    }
    .feature-card:hover { border-color: #ab9ff2; box-shadow: 0 0 20px rgba(171, 159, 242, 0.2); }
    
    /* Заголовок градиентом */
    .hero-text {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #ab9ff2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HERO SECTION ---
st.markdown('<p class="hero-text">NEXUS ARBITRAGE SYSTEM</p>', unsafe_allow_html=True)
st.write("<p style='text-align: center; font-size: 1.2rem; color: #888;'>Профессиональный терминал для арбитража в экосистеме Solana</p>", unsafe_allow_html=True)

st.divider()

# --- 3. FEATURES ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="feature-card"><h3>⚡ Speed</h3><p>Минимальная задержка благодаря прямому RPC-коннекту.</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card"><h3>🛡 Security</h3><p>Ваши API-ключи хранятся локально. Полный контроль.</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card"><h3>📊 Analytics</h3><p>Интеграция с TradingView и реальные данные с Binance/Bybit.</p></div>', unsafe_allow_html=True)

st.write("##")

# --- 4. PAYMENT SECTION ---
st.write("### 💎 Активация лицензии")
c_left, c_right = st.columns([1.5, 1])

with c_left:
    st.info("""
    **Что входит в Pro-версию:**
    * Доступ к Scanner Engine v24.1
    * Автоматическое исполнение ордеров (Sell-Market)
    * Логирование всех операций в реальном времени
    * Приоритетная поддержка 24/7
    """)

with c_right:
    # Здесь наша Web3 кнопка
    user_id = st.query_params.get("user_id", "Guest")
    st.markdown(f"**Лицензия для ID:** `{user_id}`")
    st.markdown("**Стоимость:** `0.5 SOL`")
    
    phantom_js = f"""
    <script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.js"></script>
    <button id="pay-btn" style="
        width: 100%; padding: 20px; border-radius: 12px;
        background: linear-gradient(45deg, #ab9ff2, #4facfe);
        color: white; font-weight: bold; font-size: 1.1rem;
        border: none; cursor: pointer; box-shadow: 0 4px 15px rgba(171, 159, 242, 0.3);
    ">
        Оплатить через Phantom ⚡
    </button>

    <script>
    const btn = document.getElementById('pay-btn');
    btn.onclick = async () => {{
        const {{ solana }} = window;
        if (solana && solana.isPhantom) {{
            try {{
                const resp = await solana.connect();
                const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl("mainnet-beta"));
                const transaction = new solanaWeb3.Transaction().add(
                    solanaWeb3.SystemProgram.transfer({{
                        fromPubkey: resp.publicKey,
                        toPubkey: new solanaWeb3.PublicKey("BLAnMhapJrWvytv3vCdkS6hcYC88NRKi2wrUYeV4LW4w"),
                        lamports: 0.5 * 1000000000,
                    }})
                );
                transaction.feePayer = resp.publicKey;
                const {{ blockhash }} = await connection.getLatestBlockhash();
                transaction.recentBlockhash = blockhash;
                const {{ signature }} = await solana.signAndSendTransaction(transaction);
                alert("Транзакция отправлена! Ключ придет в бота.");
            }} catch (err) {{ alert("Ошибка: " + err.message); }}
        }} else {{ alert("Установите Phantom!"); }}
    }};
    </script>
    """
    components.html(phantom_js, height=100)

st.divider()
st.caption("© 2026 Nexus Systems. Built for the Solana Ecosystem.")
