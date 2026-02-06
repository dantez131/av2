import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("➡️ /start получен на сервере")
    try:
        await update.message.reply_text("✅ ТЕСТ: бот отвечает на /start")
        print("✅ Ответ пользователю отправлен")
    except Exception as e:
        print(f"❌ Ошибка при ответе: {e}")

def main():
    print("🚀 Бот запускается...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot started and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
