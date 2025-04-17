import requests
import Telegram as tb
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


class TelegramMessanger():
    def __init__(self):
        self.BOT_TOKEN = None
        self.chatID = None
        
        pass
    
    
    BOT_TOKEN = "your_bot_token"

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text=f"Your Chat ID is: {chat_id}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

    
    def send_message(self, message):
        """
        Send a message to a Telegram chat.
        :param message: The message to send.
        """
        # Your logic to send a message to Telegram goes here
        bot_token = "YOUR_API_TOKEN"
        chat_id = "YOUR_CHAT_ID"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id, 
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
