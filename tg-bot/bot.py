import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import MemorySession

# ===========================
# ПЕРЕМЕННЫЕ (НАСТРОЙКИ)
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Твои чаты (ты их уже дал)
LOG_CHAT_ID = -1003671787625        # сюда идут ВСЕ логи
POSTBACK_CHAT_ID = -1003712583340   # сюда приходят постбеки

# Регулярка, чтобы вытащить ID между ==
ID_PATTERN = re.compile(r"==(\d+)==")

# ===========================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ===========================

client = TelegramClient(
    MemorySession(),
    api_id=0,
    api_hash=""
).start(bot_token=BOT_TOKEN)

print("✅ Bot started and running...")

# ===========================
# УТИЛИТЫ
# ===========================

async def log(message: str):
    """Отправляет логи в отдельный чат"""
    try:
        await client.send_message(LOG_CHAT_ID, f"📡 LOG: {message}")
    except Exception as e:
        print(f"❌ Ошибка логирования: {e}")

# ===========================
# /START
# ===========================

@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    user_id = event.sender_id

    await log(f"Пользователь {user_id} нажал /start")

    buttons = [
        [("📱 Открыть Web App", "open_webapp")],
        [("ℹ️ Инструкция", "help")]
    ]

    await event.respond(
        "👋 Привет! Я твой основной бот.\n\n"
        "Я помогу тебе пройти регистрацию и доступ к веб-приложению.\n\n"
        "Выбери действие:",
        buttons=buttons
    )

# ===========================
# ОБРАБОТКА КНОПОК
# ===========================

@client.on(events.CallbackQuery)
async def callback_handler(event):
    user_id = event.sender_id
    data = event.data.decode()

    await log(f"Пользователь {user_id} нажал кнопку: {data}")

    if data == "help":
        await event.answer(
            "Сначала зарегистрируйся у партнёра, затем внеси депозит. "
            "После депозита я выдам тебе пароль к Web App.",
            alert=True
        )

    elif data == "open_webapp":
        await event.answer(
            "Скоро здесь будет кнопка Web App — добавим на следующем шаге.",
            alert=True
        )

# ===========================
# ЧТЕНИЕ ПОСТБЕК-ЧАТА
# ===========================

@client.on(events.NewMessage(chats=POSTBACK_CHAT_ID))
async def postback_handler(event):
    text = event.text or ""

    match = ID_PATTERN.search(text)
    if not match:
        await log(f"⚠️ Постбек без понятного ID: {text}")
        return

    user_id = int(match.group(1))

    await log(f"📩 Получен постбек для пользователя: {user_id}")

    # ПОКА ПРОСТО ЛОГ — дальше мы сюда добавим логику
    # (регистрация → депозит → выдача пароля)

# ===========================
# ЗАПУСК
# ===========================

client.run_until_disconnected()
