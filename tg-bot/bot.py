import re
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"

LOG_CHAT_ID = -1003671787625       # чат логов
POSTBACK_CHAT_ID = -1003712583340  # чат постбеков

# Три URL для трёх состояний пользователя
APP_URL_NEW = "https://aviatorbot.up.railway.app/app1"
APP_URL_REGISTERED = "https://aviatorbot.up.railway.app/app2"
APP_URL_DEPOSITED = "https://aviatorbot.up.railway.app/app3"

# ================== ЛОГИ ==================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def send_log(context: ContextTypes.DEFAULT_TYPE, text: str):
    try:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=f"📡 LOG: {text}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки лога: {e}")

# ================== ХРАНИЛИЩЕ СТАТУСОВ ==================

# Возможные статусы: "new", "registered", "deposited"
user_states = {}

# ================== УТИЛИТЫ ==================

def extract_user_id(text: str):
    """
    Извлекаем ID пользователя между == и ==
    Пример: something ==528202393== something
    """
    match = re.search(r"==(\d+)==", text)
    if match:
        return int(match.group(1))
    return None

def get_main_keyboard(user_id: int):
    """Клавиатура с WebApp-кнопкой в зависимости от статуса"""
    status = user_states.get(user_id, "new")

    if status == "new":
        webapp_url = APP_URL_NEW
    elif status == "registered":
        webapp_url = APP_URL_REGISTERED
    else:  # deposited
        webapp_url = APP_URL_DEPOSITED

    keyboard = [
        [KeyboardButton(
            text="Открыть приложение",
            web_app=WebAppInfo(url=webapp_url)
        )],
        [KeyboardButton("Помощь"), KeyboardButton("Мой статус")]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================== /START ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = "new"

    await send_log(context, f"▶️ Пользователь {user_id} нажал /start")

    await update.message.reply_text(
        "👋 Добро пожаловать! Используйте меню внизу 👇",
        reply_markup=get_main_keyboard(user_id)
    )

# ================== ОБРАБОТКА КНОПОК ==================

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await send_log(context, f"ℹ️ Пользователь {user_id} нажал ПОМОЩЬ")

    await update.message.reply_text(
        "📖 Инструкция:\n\n"
        "1️⃣ Зарегистрируйтесь в приложении\n"
        "2️⃣ Внесите депозит\n"
        "3️⃣ Получите доступ к сервису",
        reply_markup=get_main_keyboard(user_id)
    )

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = user_states.get(user_id, "new")

    await send_log(context, f"📊 Пользователь {user_id} запросил статус")

    text_map = {
        "new": "🆕 Вы ещё не зарегистрированы.",
        "registered": "🟡 Регистрация есть, ожидаем депозит.",
        "deposited": "🟢 Депозит получен — доступ открыт!"
    }

    await update.message.reply_text(
        f"Ваш статус: {text_map.get(status, 'Неизвестный статус')}",
        reply_markup=get_main_keyboard(user_id)
    )

# ================== ОБРАБОТКА ПОСТБЕКОВ ==================

async def postback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Работает только в чате постбеков
    if update.effective_chat.id != POSTBACK_CHAT_ID:
        return

    text = update.message.text or ""
    user_id = extract_user_id(text)

    await send_log(context, f"📨 Получен постбек: {text}")

    if not user_id:
        await send_log(context, "❌ Не удалось извлечь user_id из постбека")
        return

    # Регистрация
    if "registration" in text.lower() or "reg" in text.lower():
        user_states[user_id] = "registered"

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Регистрация подтверждена! Теперь внесите депозит.",
                reply_markup=get_main_keyboard(user_id)
            )
            await send_log(context, f"✅ Пользователь {user_id} → статус REGISTERED")
        except Exception as e:
            await send_log(context, f"❌ Не смог написать пользователю {user_id}: {e}")

    # Депозит
    elif "deposit" in text.lower() or "dep" in text.lower():
        user_states[user_id] = "deposited"

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 Депозит получен! Вам открыт доступ к приложению.",
                reply_markup=get_main_keyboard(user_id)
            )
            await send_log(context, f"✅ Пользователь {user_id} → статус DEPOSITED")
        except Exception as e:
            await send_log(context, f"❌ Не смог написать пользователю {user_id}: {e}")

# ================== ЗАПУСК БОТА ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("Помощь"), help_handler))
    app.add_handler(MessageHandler(filters.Text("Мой статус"), status_handler))

    # Слушаем только чат постбеков
    app.add_handler(MessageHandler(filters.Chat(POSTBACK_CHAT_ID), postback_handler))

    print("🚀 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
