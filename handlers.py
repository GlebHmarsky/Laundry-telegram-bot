from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from storage import load_data, save_data
from data import laundry_groups,users_laundry


def start(update: Update, context: CallbackContext):
    menu_text = (
        "Welcome to the Laundry Organizer! Here are the available commands:\n\n"
        "/addlaundry - Add a laundry item\n"
        "/matchlaundry - Find laundry matches\n"
        "/showlaundry - Show your added laundry\n"
        "/showlaundry all - Show all added laundry by everyone\n"
        # Add more lines for other available commands
    )
    update.message.reply_text(menu_text)


def add_laundry(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users_laundry:
        users_laundry[user_id] = {"white": 0, "colored": 0, "black": 0}

    color_keyboard = [
        [KeyboardButton("White", callback_data=f"white_{user_id}")],
        [KeyboardButton("Colored", callback_data=f"colored_{user_id}")],
        [KeyboardButton("Black", callback_data=f"black_{user_id}")]
    ]
    reply_markup = ReplyKeyboardMarkup(color_keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Choose the color of the laundry item you want to add:", reply_markup=reply_markup)


def add_color(update: Update, context: CallbackContext):
    color = update.message.text.lower()
    user_id = str(update.message.from_user.id)

    # Load the current laundry data.
    laundry_data = load_data()

    # If the user is not in the laundry_data, create an entry for them.
    if user_id not in laundry_data:
        laundry_data[user_id] = {'white': 0, 'colored': 0, 'black': 0}

    # Add the laundry item to the user's data.
    laundry_data[user_id][color] += 1

    # Save the updated laundry data.
    save_data(laundry_data)

    update.message.reply_text(f"Added 1 {color} item to your laundry list. Use /addlaundry to add more items.", reply_markup=ReplyKeyboardRemove())

def show_laundry(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    show_all = 'all' in context.args

    # Load the current laundry data.
    laundry_data = load_data()

    if show_all:
        if not laundry_data:
            update.message.reply_text("No laundry items have been added by any user.")
            return

        laundry_message = "Here's the laundry added by everyone:\n\n"
        for user, user_laundry in laundry_data.items():
            laundry_message += f"User {user}:\n"
            for color, count in user_laundry.items():
                laundry_message += f"{color.capitalize()}: {count}\n"
            laundry_message += "\n"
    else:
        # Check if the user has any laundry data.
        if user_id not in laundry_data:
            update.message.reply_text("You haven't added any laundry items yet.")
            return

        # Create a message with the user's laundry data.
        user_laundry = laundry_data[user_id]
        laundry_message = "Here's your added laundry:\n"
        for color, count in user_laundry.items():
            laundry_message += f"{color.capitalize()}: {count}\n"

    update.message.reply_text(laundry_message)




def match_laundry(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users_laundry:
        update.message.reply_text(
            "You haven't added any laundry items yet. Use /addlaundry to add items.")
        return

    user_laundry = users_laundry[user_id]
    matched_colors = []
    for color, count in user_laundry.items():
        if count > 0 and len(laundry_groups[color]) > 1:
            matched_colors.append(color)
    if matched_colors:
        response = "You have matched laundry groups for the following colors:\n"
        for color in matched_colors:
            group_members = [str(user)
                             for user in laundry_groups[color] if user != user_id]
            response += f"{color.capitalize()}: {', '.join(group_members)}\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text(
            "No matches found for your laundry. Add more items with /addlaundry or wait for others to join.")