import os
import asyncio
import aiosqlite
import requests
import threading
import time
import secrets
import string
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = '8664053850:AAHVeTustwsTtDZMoIO0D-HHBbv11vjvJj8'
ADMIN_ID = 5000679554
DB_PATH = "nexus_hub.db"
SOL_ADDRESS = "BLAnMhapJrWvytv3vCdkS6hcYC88NRKi2wrUYeV4LW4w" 
WEBHOOK_PORT = 8081 

# URL твоего сайта оплаты (если используешь Deep Link напрямую, оставь как ниже)
# Но лучше, если это будет ссылка на твой Streamlit pay_site.py
PAY_SITE_URL = f"https://phantom.app/ul/v1/transfer?recipient={SOL_ADDRESS}&amount=0.5&label=NexusPro"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- [ UTILS ] ---
def generate_license_key():
    prefix = "NXS"
    chars = string.ascii_uppercase + string.digits
    key = '-'.join([''.join(secrets.choice(chars) for _ in range(4)) for _ in range(3)])
    return f"{prefix}-{key}"

# --- [ DATABASE ] ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                service TEXT,
                status TEXT DEFAULT 'pending',
                license_key TEXT UNIQUE,
                timestamp TEXT
            )
        ''')
        await db.commit()
        print("📁 Database Ready.")

# --- [ WEBHOOK: ГЕНЕРАЦИЯ КЛЮЧА ПОСЛЕ ОПЛАТЫ ] ---
async def handle_payment_notification(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        new_key = generate_license_key()
        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE orders SET status = 'paid', license_key = ? WHERE user_id = ? AND status = 'pending'",
                (new_key, user_id)
            )
            await db.commit()

        await bot.send_message(
            user_id, 
            f"✅ **ОПЛАТА ПОЛУЧЕНА!**\n\n🔑 Твой ключ: `{new_key}`\n\n🚀 Активируй его в Nexus Terminal.",
            parse_mode="Markdown"
        )
        return web.json_response({"status": "delivered"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def start_webhook_server():
    app = web.Application()
    app.router.add_post('/webhook/payment', handle_payment_notification)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', WEBHOOK_PORT)
    await site.start()

# --- [ BOT HANDLERS ] ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Купить Nexus Pro (0.5 SOL)", callback_data="buy_nexus")],
        [InlineKeyboardButton(text="👨‍💻 Support", url="https://t.me/wyr1xl")]
    ])
    await message.answer(
        "🦅 **NEXUS HUB v5.7**\n━━━━━━━━━━━━━━━━━━━━\nСистема автоматической активации лицензий через Solana Pay.",
        reply_markup=kb, parse_mode="Markdown"
    )

@dp.callback_query(F.data == "buy_nexus")
async def process_buy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # 1. Сначала логируем попытку в БД
    async with aiosqlite.connect(DB_PATH) as db:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute(
            "INSERT INTO orders (user_id, username, service, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, callback.from_user.username, "Nexus_Pro", ts)
        )
        await db.commit()

    # 2. Формируем ссылку для WebApp (или Deep Link)
    # Если ты хочешь открывать прямо Phantom, используй URL Deep Link
    # Если хочешь открывать свой сайт на Streamlit, замени PAY_SITE_URL
    final_pay_url = f"{PAY_SITE_URL}&memo=ID{user_id}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⚡️ Открыть Phantom Pay", 
            web_app=WebAppInfo(url=final_pay_url)
        )],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
    ])
    
    await callback.message.edit_text(
        "🚀 **Оплата через Web3**\n━━━━━━━━━━━━━━━━━━━━\n"
        "Нажми на кнопку ниже. Telegram откроет шлюз оплаты Phantom.\n\n"
        f"📍 Адрес: `{SOL_ADDRESS[:6]}...{SOL_ADDRESS[-4:]}`\n"
        "💰 Сумма: **0.5 SOL**",
        reply_markup=kb, parse_mode="Markdown"
    )

# --- MAIN ---
async def main():
    await init_db()
    await start_webhook_server()
    print("🚀 NEXUS SYSTEM STARTED...")
    await dp.start_polling(bot)
    await dp.start_polling(bot, handle_signals=False)
    
if __name__ == '__main__':
    asyncio.run(main())
    
