# Before running script be sure you install deps
# pip install python-telegram-bot

import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from handlers import add_color, start, show_laundry, add_laundry, match_laundry

logging.basicConfig(level=logging.INFO)
TOKEN = "6135601546:AAECHTEz5rso2liRcocwAot0rXClNVs6xKk"


updater = Updater(TOKEN, use_context=True)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addlaundry", add_laundry))
dispatcher.add_handler(CommandHandler("matchlaundry", match_laundry))
dispatcher.add_handler(CommandHandler("showlaundry", show_laundry))
dispatcher.add_handler(MessageHandler(
    Filters.text(["White", "Colored", "Black"]), add_color))

updater.start_polling()
updater.idle()
