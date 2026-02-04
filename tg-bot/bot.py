import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ===========================
# НАСТРОЙКИ
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG_CHAT_ID = -1003671787625       # твой лог-чат
POSTBACK_CHAT_ID = -1003712583340  # чат с постбеками

# Твой Web App (поменяем потом, если нужно)
WEBAPP_URL = "https://av2-production.up.railway.app"

# ТВОЙ СТАТИЧНЫЙ ПАРОЛЬ
WEBAPP_PASSWORD = "7300"

# ищем ID между ==...==
ID_PATTERN = re.compile(r"==(\d+)==")

# Хранилище статусов пользователей (в памяти)
user_status = {}
# возможные статусы:
# "new" -> ничего нет
# "registered" -> есть регистрация
# "deposited" -> есть депозит (доступ выдан)

# ===========================
# УТИЛИТА ДЛЯ ЛОГОВ
# ===========================

async def send_log(app: Application, text: str):
    try:
        await app.bot.send_message(chat_id=LOG_CHAT_ID, text=f"📡 LOG: {text}")
    except Exception as e:
        print(f"Ошибка логирования: {e}")

# ===========================
# /START
# ===========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_status.setdefault(user_id, "new")

    await send_log(context.application, f"Пользователь {user_id} нажал /start (статус: {user_status[user_id]})")

    keyboard = [
        [InlineKeyboardButton(
            "📱 Открыть Web App",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )],
        [InlineKeyboardButton("ℹ️ Инструкция", callback_data="help")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Привет! Я твой основной бот.\n\n"
        "1️⃣ Сначала зарегистрируйся у партнёра.\n"
        "2️⃣ Затем внеси депозит.\n"
        "3️⃣ После депозита я выдам тебе пароль к Web App.\n\n"
        "Можешь уже открыть Web App, но доступ появится после депозита.",
        reply_markup=reply_markup,
    )

# ===========================
# ОБРАБОТКА КНОПОК
# ===========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await send_log(context.application, f"Пользователь {user_id} нажал кнопку: {data}")

    if data == "help":
        await query.answer(
            "1) Пройди регистрацию.\n"
            "2) Внеси депозит.\n"
            "После этого я пришлю тебе пароль.",
            show_alert=True,
        )

# ===========================
# ЧТЕНИЕ ПОСТБЕК-ЧАТА
# ===========================

async def postback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # реагируем ТОЛЬКО на нужный чат
    if update.effective_chat.id != POSTBACK_CHAT_ID:
        return

    text = update.message.text or ""

    match = ID_PATTERN.search(text)
    if not match:
        await send_log(context.application, f"⚠️ Постбек без понятного ID: {text}")
        return

    user_id = int(match.group(1))

    # Инициализируем статус, если пользователя ещё не было
    user_status.setdefault(user_id, "new")

    # Определяем тип постбека по тексту
    text_lower = text.lower()

    # ====== 1) РЕГИСТРАЦИЯ ======
    if "registration" in text_lower or "reg" in text_lower:
        user_status[user_id] = "registered"

        await send_log(context.application, f"📩 Регистрация получена для {user_id}")

        try:
            await context.application.bot.send_message(
                chat_id=user_id,
                text="✅ Регистрация подтверждена!\n\nТеперь внеси депозит, чтобы получить доступ."
            )
        except Exception as e:
            await send_log(context.application, f"❌ Не смог написать пользователю {user_id}: {e}")

    # ====== 2) ДЕПОЗИТ ======
    elif "deposit" in text_lower or "dep" in text_lower or "amount" in text_lower:
        # Если уже выдавали доступ — не дублируем
        if user_status.get(user_id) == "deposited":
            await send_log(context.application, f"ℹ️ Депозит повторно пришёл для {user_id}, но доступ уже выдан")
            return

        user_status[user_id] = "deposited"

        await send_log(context.application, f"💰 Депозит получен для {user_id} — выдаём пароль")

        try:
            await context.application.bot.send_message(
                chat_id=user_id,
                text=f"🎉 Депозит подтверждён!\n\n"
                     f"🔑 Твой пароль для Web App:\n\n"
                     f"`{WEBAPP_PASSWORD}`\n\n"
                     f"Нажми «Открыть Web App» и введи его там.",
                parse_mode="Markdown"
            )
        except Exception as e:
            await send_log(context.application, f"❌ Не смог написать пользователю {user_id}: {e}")

    else:
        await send_log(context.application, f"ℹ️ Неизвестный постбек для {user_id}: {text}")

# ===========================
# ЗАПУСК БОТА
# ===========================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, postback_handler))

    print("✅ Bot started and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
