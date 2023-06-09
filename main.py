# Before running script be sure you install deps
# pip install python-telegram-bot

import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from handlers import handle_user_message, edit_laundry, start, handle_yes_no_button, show_laundry, add_laundry, match_laundry, button_handler, color_selected
from secret_token import TOKEN

logging.basicConfig(level=logging.INFO)

updater = Updater(TOKEN, use_context=True)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addlaundry", add_laundry))
dispatcher.add_handler(CommandHandler("matchlaundry", match_laundry))
dispatcher.add_handler(CommandHandler("showlaundry", show_laundry))
dispatcher.add_handler(CommandHandler("editlaundry", edit_laundry))
dispatcher.add_handler(CallbackQueryHandler(color_selected, pattern="^match:"))
dispatcher.add_handler(MessageHandler(
    Filters.text & ~Filters.command, handle_user_message))

dispatcher.add_handler(CallbackQueryHandler(
    handle_yes_no_button, pattern="^(yes|no):"))

dispatcher.add_handler(CallbackQueryHandler(button_handler))

updater.start_polling()
updater.idle()
