import streamlit as st
import streamlit.components.v1 as components

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Nexus Web3 Pay", page_icon="⚡", layout="centered")

# Данные для оплаты
DESTINATION_ADDRESS = "BLAnMhapJrWvytv3vCdkS6hcYC88NRKi2wrUYeV4LW4w"
PRICE_SOL = 0.5

# Стилизация под твой бренд (темная тема, неон)
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    .pay-card {
        padding: 30px;
        border-radius: 20px;
        background: rgba(171, 159, 242, 0.05);
        border: 1px solid #ab9ff2;
        text-align: center;
        box-shadow: 0 0 20px rgba(171, 159, 242, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Получаем ID пользователя из URL (например, my-site.com/?user_id=12345)
query_params = st.query_params
user_id = query_params.get("user_id", "Unknown")

st.markdown(f"""
<div class="pay-card">
    <h1>⚡ NEXUS PRO</h1>
    <p style="color: #ab9ff2; font-size: 1.2rem;">Активация лицензии</p>
    <hr style="border-color: #333;">
    <p>Пользователь: <b>{user_id}</b></p>
    <p>К оплате: <span style="font-size: 1.5rem; color: #00ffcc;">{PRICE_SOL} SOL</span></p>
</div>
""", unsafe_allow_html=True)

# JS-код для коннекта с Phantom и отправки транзакции
phantom_logic = f"""
<script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.js"></script>
<div style="margin-top: 25px;">
    <button id="pay-btn" style="
        width: 100%; padding: 18px; border-radius: 12px;
        background: linear-gradient(45deg, #ab9ff2, #4facfe);
        color: white; font-weight: bold; font-size: 18px;
        border: none; cursor: pointer; transition: 0.3s;
    ">
        Оплатить через Phantom ⚡
    </button>
</div>

<script>
const btn = document.getElementById('pay-btn');
const dest = "{DESTINATION_ADDRESS}";
const amount = {PRICE_SOL} * 1000000000; // перевод в лампорты

btn.onclick = async () => {{
    const {{ solana }} = window;
    
    if (solana && solana.isPhantom) {{
        try {{
            const resp = await solana.connect();
            const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl("mainnet-beta"));
            
            const transaction = new solanaWeb3.Transaction().add(
                solanaWeb3.SystemProgram.transfer({{
                    fromPubkey: resp.publicKey,
                    toPubkey: new solanaWeb3.PublicKey(dest),
                    lamports: amount,
                }})
            );
            
            transaction.feePayer = resp.publicKey;
            const {{ blockhash }} = await connection.getLatestBlockhash();
            transaction.recentBlockhash = blockhash;
            
            const {{ signature }} = await solana.signAndSendTransaction(transaction);
            
            // Визуальное подтверждение
            btn.innerText = "✅ Оплачено!";
            btn.style.background = "#00ffcc";
            alert("Транзакция отправлена в блокчейн! Хэш: " + signature);
            
        }} catch (err) {{
            alert("Ошибка оплаты: " + err.message);
        }}
    }} else {{
        alert("Кошелек Phantom не найден!");
        window.open("https://phantom.app/", "_blank");
    }}
}};
</script>
"""

components.html(phantom_logic, height=150)

st.caption("После аппрува в кошельке, Nexus Watcher зафиксирует транзакцию и пришлет ключ в Telegram.")
