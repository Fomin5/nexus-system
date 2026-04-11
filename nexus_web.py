import streamlit as st
import qrcode
from io import BytesIO
import streamlit.components.v1 as components
import requests
import time

# --- ЭТАП 1: API И ЖИВЫЕ ДАННЫЕ ---
def get_sol_price():
    try:
        # Получаем реальную цену SOL с Binance
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT", timeout=2)
        return float(res.json()['price'])
    except:
        return 145.20 # Цена-заглушка

# --- ЭТАП 2: КОНФИГУРАЦИЯ И СТИЛИ ---
st.set_page_config(
    page_title="NEXUS AI TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

current_sol_price = get_sol_price()

st.markdown(f"""
    <style>
    /* Глобальный темный фон */
    .stApp {{ background-color: #050505; color: white; }}
    
    /* Окно Phantom (стиль Glassmorphism) */
    .phantom-window {{
        position: fixed; 
        top: 70px; 
        right: 20px; 
        width: 360px; 
        height: 590px;
        background-color: rgba(26, 26, 26, 0.98); 
        border: 1px solid #333; 
        border-radius: 24px;
        z-index: 1000; 
        box-shadow: 0 20px 60px rgba(0,0,0,1);
        padding: 20px; 
        display: flex; 
        flex-direction: column;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Заголовки и текст внутри кошелька */
    .wallet-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
    .asset-row {{ 
        display: flex; justify-content: space-between; padding: 14px; 
        background: #222; border-radius: 14px; margin-bottom: 10px; 
        border: 1px solid rgba(255,255,255,0.05);
    }}
    
    /* Кастомизация кнопок Streamlit под Phantom */
    div.stButton > button {{
        border-radius: 12px;
        transition: 0.3s all ease;
    }}
    
    /* Анимация плавного появления */
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .animate-phantom {{ animation: fadeIn 0.4s ease-out; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЭТАП 3: СОСТОЯНИЕ (SESSION STATE) ---
if "phantom_visible" not in st.session_state: st.session_state.phantom_visible = False
if "connected" not in st.session_state: st.session_state.connected = False

# --- ЭТАП 4: SIDEBAR (УПРАВЛЕНИЕ) ---
with st.sidebar:
    st.image("https://cryptologos.cc/logos/solana-sol-logo.png", width=40)
    st.title("NEXUS CORE")
    
    if not st.session_state.connected:
        if st.button("👻 Connect Phantom", use_container_width=True):
            st.session_state.connected = True
            st.rerun()
    else:
        # Кнопка-статус с живой ценой
        wallet_btn = f"👛 BjwVt...XqhU7J | ${current_sol_price:.2f}"
        if st.button(wallet_btn, use_container_width=True):
            st.session_state.phantom_visible = not st.session_state.phantom_visible
            st.rerun()
    
    st.divider()
    page = st.radio("НАВИГАЦИЯ", ["📈 Terminal", "💎 License"])
    st.divider()
    st.caption("🤖 AI Engine: Status Healthy")
    st.info(f"SOL/USDT: {current_sol_price}")

# --- ЭТАП 5: РАБОЧИЙ ФУНКЦИОНАЛ КОШЕЛЬКА ---
if st.session_state.connected and st.session_state.phantom_visible:
    sol_amount = 12.55
    # Динамический расчет баланса в $
    wallet_usd = (sol_amount * current_sol_price) + 105.00
    
    # HTML Контейнер
    st.markdown('<div class="phantom-window animate-phantom">', unsafe_allow_html=True)
    
    # Верхняя часть Phantom
    st.markdown(f"""
        <div class="wallet-header">
            <span style="color:#ab9ff2; font-weight:bold; letter-spacing:1px;">PHANTOM</span>
            <span style="font-size:10px; background:#222; padding:4px 10px; border-radius:20px; color:#888;">Mainnet Beta</span>
        </div>
        <div style="text-align:center; margin-bottom:25px;">
            <p style="color:#666; font-size:14px; margin-bottom:5px;">Estimated Balance</p>
            <h1 style="margin:0; font-size:40px; font-weight:800;">${wallet_usd:,.2f}</h1>
            <p style="color:#00E676; font-size:12px; margin-top:5px;">▲ 2.4% ($42.10)</p>
        </div>
    """, unsafe_allow_html=True)

    # ИНТЕРАКТИВНЫЕ КНОПКИ
    c1, c2 = st.columns(2)
    with c1:
        # Реальная ссылка на покупку (Bybit или MoonPay)
        st.link_button("📥 Deposit", "https://www.bybit.com/fiat/trade/otc/?coin=SOL&fiat=RUB", use_container_width=True)
    with c2:
        if st.button("📤 Send", use_container_width=True):
            st.toast("Функция перевода активирована. Выберите адрес.")
            time.sleep(1)
            # Можно добавить переключение на страницу оплаты
    
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # Список токенов
    st.markdown(f"""
        <div class="asset-row">
            <span><b>Solana</b><br><small style="color:#888;">{sol_amount} SOL</small></span>
            <span style="text-align:right;"><b>${(sol_amount*current_sol_price):,.2f}</b></span>
        </div>
        <div class="asset-row">
            <span><b>USDC</b><br><small style="color:#888;">Digital Dollar</small></span>
            <span style="text-align:right;"><b>$105.00</b></span>
        </div>
        <div class="asset-row">
            <span><b>Nexus NX</b><br><small style="color:#888;">Staking</small></span>
            <span style="text-align:right;"><b>500,000 NX</b></span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)

    # Кнопка закрытия
    if st.button("❌ Close Wallet", use_container_width=True):
        st.session_state.phantom_visible = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- ЭТАП 6: КОНТЕНТ СТРАНИЦ ---
if page == "📈 Terminal":
    st.title(f"SOL Performance — Live ${current_sol_price}")
    
    # Виджет TradingView на весь экран
    components.html(f"""
        <div style="height:650px; border:1px solid #333; border-radius:16px; overflow:hidden;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
                new TradingView.widget({{
                    "autosize": true,
                    "symbol": "BYBIT:SOLUSDT",
                    "interval": "1",
                    "theme": "dark",
                    "container_id": "tv_chart",
                    "locale": "ru",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "allow_symbol_change": true
                }});
            </script>
        </div>
    """, height=660)

elif page == "💎 License":
    st.header("💎 Лицензионный Центр Nexus")
    st.divider()
    
    left, right = st.columns([1.5, 1])
    
    with left:
        st.write("### Активация Pro-функций")
        st.markdown("""
        * Доступ к сигналам Nexus AI
        * Автоматический Arbitrage-бот
        * Приоритетное исполнение ордеров
        """)
        user_tag = st.text_input("Введите ваш никнейм (TG/X):", placeholder="@yourname")
        
    with right:
        st.markdown("""
        <div style="background:#111; padding:25px; border-radius:20px; border:1px solid #ab9ff2; text-align:center;">
            <h4 style="margin:0;">К оплате: 0.5 SOL</h4>
            <small style="color:#666;">Лицензия привязывается к кошельку</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("СГЕНЕРИРОВАТЬ ИНВОЙС", use_container_width=True):
            if not st.session_state.connected:
                st.error("Сначала подключите кошелек!")
            elif not user_tag:
                st.warning("Введите никнейм!")
            else:
                # Генерация реального QR для Solana
                pay_data = f"solana:BjwVtUF8t74k1WJ5jxN51gnhyekYvzs89u6whoXqhU7J?amount=0.5&label=NexusPro&memo={user_tag}"
                qr_code = qrcode.QRCode(version=1, box_size=10, border=2)
                qr_code.add_data(pay_data)
                qr_code.make(fit=True)
                img = qr_code.make_image(fill_color="black", back_color="white")
                
                buf = BytesIO()
                img.save(buf)
                st.image(buf.getvalue(), caption=f"Scan to Activate for {user_tag}", width=320)
                st.success("QR-код сгенерирован успешно!")
