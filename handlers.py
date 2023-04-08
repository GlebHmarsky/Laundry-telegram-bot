from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from storage import load_data, save_data
from data import users_laundry


def start(update: Update, context: CallbackContext):
    menu_text = (
        "Welcome to the Laundry Organizer! Here are the available commands:\n\n"
        "/addlaundry - Add a laundry item\n"
        "/matchlaundry - Find laundry matches\n"
        "/showlaundry - Show your added laundry\n"
        "/showlaundry all - Show all added laundry by everyone\n"
        "/editlaundry - Allows edit your laundry\n"
        # Add more lines for other available commands
    )
    update.message.reply_text(menu_text)


# Okay, i need to extend functionality of adding new color, i need to do next:
# When user select color after that

def add_laundry(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # If user not in list
    if user_id not in users_laundry:
        users_laundry[user_id] = {"white": 0, "colored": 0, "black": 0}

    keyboard = [
        [
            InlineKeyboardButton("White", callback_data="white"),
            InlineKeyboardButton("Colored", callback_data="colored"),
            InlineKeyboardButton("Black", callback_data="black")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Choose a color for your laundry:", reply_markup=reply_markup)


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = str(query.from_user.id)
    users_laundry = load_data()

    color_data = ["white", "colored", "black"]

    if query.data in color_data:
        context.user_data['selected_color'] = query.data

        keyboard = [
            [
                InlineKeyboardButton("1/5", callback_data="quantity_1"),
                InlineKeyboardButton("2/5", callback_data="quantity_2"),
                InlineKeyboardButton("3/5", callback_data="quantity_3"),
                InlineKeyboardButton("4/5", callback_data="quantity_4"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            "How many laundry items do you want to add?", reply_markup=reply_markup)
    elif query.data.startswith("quantity_"):
        quantity = int(query.data.split("_")[1])

        if user_id not in users_laundry:
            users_laundry[user_id] = {}

        color = context.user_data['selected_color']
        if color not in users_laundry[user_id]:
            users_laundry[user_id][color] = quantity
        else:
            users_laundry[user_id][color] += quantity

        save_data(users_laundry)
        query.edit_message_text(f"Added {quantity} {color} laundry items.")
    elif query.data.startswith("edit_"):
        color = query.data[5:]
        context.user_data['selected_color'] = color

        keyboard = [
            [
                InlineKeyboardButton("1/5", callback_data="new_quantity_1"),
                InlineKeyboardButton("2/5", callback_data="new_quantity_2"),
                InlineKeyboardButton("3/5", callback_data="new_quantity_3"),
                InlineKeyboardButton("4/5", callback_data="new_quantity_4"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f"Enter the new quantity for {color.capitalize()} laundry items:", reply_markup=reply_markup)
    elif query.data.startswith("new_quantity_"):
        new_quantity = int(query.data.split("_")[2])

        user_id = str(query.from_user.id)
        users_laundry = load_data()
        user_laundry = users_laundry[user_id]

        color = context.user_data['selected_color']
        user_laundry[color] = new_quantity
        save_data(users_laundry)

        query.edit_message_text(
            f"Updated {color.capitalize()} laundry items to {new_quantity}.")


def edit_laundry(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users_laundry = load_data()

    if user_id not in users_laundry:
        update.message.reply_text(
            "You haven't added any laundry items yet. Use /addlaundry to add items.")
        return

    user_laundry = users_laundry[user_id]
    laundry_text = "Your current laundry items:\n"
    for color, count in user_laundry.items():
        laundry_text += f"{color.capitalize()}: {count}\n"
    update.message.reply_text(laundry_text)

    keyboard = [
        [
            InlineKeyboardButton("White", callback_data="edit_white"),
            InlineKeyboardButton("Colored", callback_data="edit_colored"),
            InlineKeyboardButton("Black", callback_data="edit_black"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Select the color you want to edit:", reply_markup=reply_markup)


def add_color(update: Update, context: CallbackContext):
    color = update.message.text.lower()
    user_id = str(update.message.from_user.id)

    # Load the current laundry data.
    users_laundry = load_data()

    # If the user is not in the laundry_data, create an entry for them.
    if user_id not in users_laundry:
        users_laundry[user_id] = {'white': 0, 'colored': 0, 'black': 0}

    # Add the laundry item to the user's data.
    users_laundry[user_id][color] += 1

    # Save the updated laundry data.
    save_data(users_laundry)

    update.message.reply_text(
        f"Added 1 {color} item to your laundry list. Use /addlaundry to add more items.", reply_markup=ReplyKeyboardRemove())


def show_laundry(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    show_all = 'all' in context.args

    # Load the current laundry data.
    users_laundry = load_data()

    if show_all:
        if not users_laundry:
            update.message.reply_text(
                "No laundry items have been added by any user.")
            return

        laundry_message = "Here's the laundry added by everyone:\n\n"
        for user_id, user_laundry in users_laundry.items():
            laundry_message += f"User {get_user_name(user_id, context)} (id: {user_id}):\n"
            for color, count in user_laundry.items():
                laundry_message += f"{color.capitalize()}: {count}\n"
            laundry_message += "\n"
    else:
        # Check if the user has any laundry data.
        if user_id not in users_laundry:
            update.message.reply_text(
                "You haven't added any laundry items yet.")
            return

        # Create a message with the user's laundry data.
        user_laundry = users_laundry[user_id]
        laundry_message = "Here's your added laundry:\n"
        for color, count in user_laundry.items():
            laundry_message += f"{color.capitalize()}: {count}\n"

    update.message.reply_text(laundry_message)


def match_laundry(update: Update, context: CallbackContext):
    users_laundry = load_data()
    main_user_id = str(update.message.from_user.id)

    if main_user_id not in users_laundry:
        update.message.reply_text(
            "You haven't added any laundry items yet. Use /addlaundry to add items.")
        return

    user_laundry = users_laundry[main_user_id]
    other_users_laundry = {key: value for key,
                           value in users_laundry.items() if key != main_user_id}
    matched_colors = []

    laundry_groups = {}  # "white": [], "colored": [], "black": []

    for main_user_color, main_user_count in user_laundry.items():
        add_id_to_array(laundry_groups, main_user_color, main_user_id)
        for someone_user_id in other_users_laundry:
            someone_laundry = other_users_laundry[someone_user_id]
            if main_user_count > 0:
                if someone_laundry[main_user_color] > 0:
                    add_id_to_array(
                        laundry_groups, main_user_color, someone_user_id)
                    matched_colors.append(
                        f"Color: {main_user_color} User: {someone_user_id}")

    if matched_colors:
        response = "You have matched laundry groups for the following colors:"
        # for color in matched_colors:
        #     response += f"{color}\n"
        # update.message.reply_text(response)

        # response = "Users by color:"
        for color in laundry_groups:
            users_group = laundry_groups[color]
            response += f"\n\nColor: {color} ->"
            for user_id in users_group:
                user_chat = context.bot.get_chat(user_id)
                response += f"\n@{user_chat.username}"

        update.message.reply_text(response)

    # Sending messages
    # for color, users_group in laundry_groups.items():
    #     for user_id in users_group:
    #         send_other_participants(
    #             color, users_group, user_id, context=context)

    else:
        update.message.reply_text(
            "No matches found for your laundry. Add more items with /addlaundry or wait for others to join.")


def send_other_participants(color, users_group, send_user_id, context: CallbackContext):
    text_message = "Test, don't worry - be happy ^_^ \n"

    text_message += f"\nThere is a match on color: \"{color}\" with ->"
    for user_id in users_group:
        user_chat = context.bot.get_chat(user_id)
        text_message += "\n"
        if user_chat.first_name != "":
            text_message += f"{user_chat.first_name} "
        if user_chat.last_name != "":
            text_message += f"{user_chat.last_name} "

        text_message += f"(@{user_chat.username})"

    context.bot.send_message(send_user_id, text_message)


def add_id_to_array(dictionary, key, id_value):
    if key not in dictionary:
        # Initialize the key with a list containing the ID
        dictionary[key] = [id_value]
    else:
        # Add the ID to the existing list
        dictionary[key].append(id_value)


def get_user_name(user_id, context):
    user_chat = context.bot.get_chat(user_id)
    if (user_chat.first_name):
        username = f"{user_chat.first_name} {user_chat.last_name}" if user_chat.last_name else user_chat.first_name
    else:
        username = user_chat.username

    return username
