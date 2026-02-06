import re
import asyncio
from telethon import TelegramClient, events, Button

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"

# Чаты
LOG_CHAT_ID = -1003671787625        # чат логов
POSTBACK_CHAT_ID = -1003712583340   # чат постбеков

# WEB APP URL (три состояния)
APP_URL_NEW = "https://aviatorbot.up.railway.app/app1"
APP_URL_REGISTERED = "https://aviatorbot.up.railway.app/app2"
APP_URL_DEPOSITED = "https://aviatorbot.up.railway.app/app3"

# ================== ИНИЦИАЛИЗАЦИЯ ==================

client = TelegramClient("bot", api_id=0, api_hash="").start(bot_token=BOT_TOKEN)

# Хранилище состояний пользователей
# Возможные значения: "new", "registered", "deposited"
user_states = {}

# ================== УТИЛИТЫ ==================

async def log(text: str):
    """Отправка логов в отдельный чат"""
    try:
        await client.send_message(LOG_CHAT_ID, f"📡 LOG: {text}")
    except Exception as e:
        print("Ошибка логирования:", e)

def extract_user_id(text: str):
    """
    Извлекаем ID пользователя между == и ==
    Пример:  something ==528202393== something
    """
    match = re.search(r"==(\d+)==", text)
    if match:
        return int(match.group(1))
    return None

def get_main_keyboard(user_id: int):
    """Динамическая клавиатура в зависимости от статуса"""
    status = user_states.get(user_id, "new")

    if status == "new":
        webapp_url = APP_URL_NEW
    elif status == "registered":
        webapp_url = APP_URL_REGISTERED
    else:  # deposited
        webapp_url = APP_URL_DEPOSITED

    return [
        [Button.web_app("Открыть приложение", webapp_url)],
        [Button.text("Помощь"), Button.text("Мой статус")]
    ]

# ================== /START ==================

@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    user_id = event.sender_id
    user_states[user_id] = "new"

    await log(f"▶️ Пользователь {user_id} нажал /start")

    await event.respond(
        "👋 Добро пожаловать! Используйте меню внизу 👇",
        buttons=get_main_keyboard(user_id)
    )

# ================== ОБРАБОТКА КНОПОК ==================

@client.on(events.NewMessage(pattern="Помощь"))
async def help_handler(event):
    user_id = event.sender_id

    await log(f"ℹ️ Пользователь {user_id} нажал ПОМОЩЬ")

    await event.respond(
        "📖 Инструкция:\n\n"
        "1️⃣ Зарегистрируйтесь в приложении\n"
        "2️⃣ Внесите депозит\n"
        "3️⃣ Получите доступ к сервису",
        buttons=get_main_keyboard(user_id)
    )

@client.on(events.NewMessage(pattern="Мой статус"))
async def status_handler(event):
    user_id = event.sender_id
    status = user_states.get(user_id, "new")

    await log(f"📊 Пользователь {user_id} запросил статус")

    text = {
        "new": "🆕 Вы ещё не зарегистрированы.",
        "registered": "🟡 Регистрация есть, ожидаем депозит.",
        "deposited": "🟢 Депозит получен — доступ открыт!"
    }.get(status, "Неизвестный статус")

    await event.respond(
        f"Ваш статус: {text}",
        buttons=get_main_keyboard(user_id)
    )

# ================== ОБРАБОТКА ПОСТБЕКОВ ==================

@client.on(events.NewMessage(chats=POSTBACK_CHAT_ID))
async def postback_handler(event):
    text = event.raw_text
    user_id = extract_user_id(text)

    await log(f"📨 Получен постбек: {text}")

    if not user_id:
        await log("❌ Не удалось извлечь user_id из постбека")
        return

    # Определяем тип постбека
    if "registration" in text.lower() or "reg" in text.lower():
        user_states[user_id] = "registered"

        try:
            await client.send_message(
                user_id,
                "✅ Регистрация подтверждена! Теперь внесите депозит.",
                buttons=get_main_keyboard(user_id)
            )
            await log(f"✅ Пользователь {user_id} → статус REGISTERED")
        except Exception as e:
            await log(f"❌ Не смог написать пользователю {user_id}: {e}")

    elif "deposit" in text.lower() or "dep" in text.lower():
        user_states[user_id] = "deposited"

        try:
            await client.send_message(
                user_id,
                "🎉 Депозит получен! Вам открыт доступ к приложению.",
                buttons=get_main_keyboard(user_id)
            )
            await log(f"✅ Пользователь {user_id} → статус DEPOSITED")
        except Exception as e:
            await log(f"❌ Не смог написать пользователю {user_id}: {e}")

# ================== ЗАПУСК ==================

print("🚀 Бот запущен...")
client.run_until_disconnected()
