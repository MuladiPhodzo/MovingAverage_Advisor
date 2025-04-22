import venv
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
import requests

class TelegramMessenger:
    def __init__(self, chat_id=None):
        self.BOT_TOKEN = "TOKEN"  # 🛠️ Use environment variable or provided token
        self.chat_id = chat_id
        self.should_run = True  # 🔁 Flag to control bot execution

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.chat_id = chat_id
        self.should_run = True
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Advisor started.\nChat ID: {chat_id}")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.should_run = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Advisor stopped by user.")

    def run_bot(self):
        """
        Starts the Telegram bot and waits for commands.
        """
        app = Application.builder().token(self.BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("stop", self.stop))  # 🆕 Add stop command

        print("🤖 Bot is running. Use /start to begin and /stop to stop the advisor.")
        app.run_polling()

    def send_message(self, message):
        if not self.chat_id:
            print("❌ Chat ID not set. Use /start on your bot first.")
            return

        url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("✅ Message sent successfully")
            else:
                print(f"❌ Failed to send message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Exception occurred while sending message: {e}")
