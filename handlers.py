from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from typing import List

from storage import load_data, save_data
from data import users_laundry, groups_by_main_user, groups_washing, Participant


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
                InlineKeyboardButton("0", callback_data="new_quantity_0"),
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


def build_color_buttons(laundry_groups):
    buttons = []
    for color in laundry_groups:
        button = InlineKeyboardButton(
            text=color, callback_data=f"match:{color}")
        buttons.append(button)
    return buttons


def send_color_selection_message(update, context, laundry_groups):
    keyboard = build_color_buttons(laundry_groups)
    reply_markup = InlineKeyboardMarkup.from_row(keyboard)
    update.message.reply_text(
        "Select a color you want wash:",
        reply_markup=reply_markup
    )


def create_participants(laundry_group):
    participants: List[Participant] = []
    for user_id in laundry_group:
        participants.append({"ready": None, "quantity": 1, "user_id": user_id})
    return participants


def color_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    main_user_id = str(query.from_user.id)
    selected_color = query.data.split(':')[1]
    query.answer()
    query.edit_message_text(f"Selected color: {selected_color}")

    laundry_group = groups_by_main_user[main_user_id][selected_color]

    participants = create_participants(laundry_group)
    groups_washing.append({
        "main_user": main_user_id,
        "participants": participants,
        "sent_messages": [],
        "color": selected_color,
        "notification_msg": "hemlo this is notification_msg"
    })

    for user_id in laundry_group:
        send_other_participants(main_user_id,
                                selected_color, participants, user_id, context=context)


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
        for someone_user_id in other_users_laundry:
            someone_laundry = other_users_laundry[someone_user_id]
            if main_user_count > 0:
                if someone_laundry[main_user_color] > 0:
                    add_id_to_array(
                        laundry_groups, main_user_color, someone_user_id)
                    matched_colors.append(
                        f"Color: {main_user_color} User: {someone_user_id}")
        if main_user_color in laundry_groups:
            add_id_to_array(laundry_groups, main_user_color, main_user_id)

    if matched_colors:
        response = "You have matched laundry groups for the following colors:"
        for color in laundry_groups:
            users_group = laundry_groups[color]
            response += f"\n\nColor: {color} ->"
            for user_id in users_group:
                user_chat = context.bot.get_chat(user_id)
                response += f"\n@{user_chat.username}"

        update.message.reply_text(response)
        send_color_selection_message(update, context, laundry_groups)

        groups_by_main_user[main_user_id] = laundry_groups

    else:
        update.message.reply_text(
            "No matches found for your laundry. Add more items with /addlaundry or wait for others to join.")


def handle_yes_no_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split(':')
    choice, selected_user_id = data[0], data[1]
    group = find_group_by_main_user(groups_washing, selected_user_id)

    if not group:
        return

    specific_participant = find_user_by_id(group["participants"], str(user_id))
    if specific_participant:
        specific_participant["ready"] = choice == "yes"
    else:
        print(
            f"there is {user_id} ({specific_participant}) goes for undefined")
    # Update the message text for other users
    text_message = create_text_to_participants(
        group["color"], group["participants"], context)

    for sent_message in group["sent_messages"]:
        chat_id = sent_message["chat_id"]
        message_id = sent_message["message_id"]

        # Update the message in each chat
        context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                      text=text_message, reply_markup=create_yes_no_keyboard(selected_user_id))

    query.answer()


def create_yes_no_keyboard(user_id):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"yes:{user_id}"),
            InlineKeyboardButton("No", callback_data=f"no:{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def find_group_by_main_user(groups, main_user_to_find):
    for group in groups:
        if group["main_user"] == main_user_to_find:
            return group
    return None

# TODO: change it for DICT!


def find_user_by_id(list, user_to_find):
    for part in list:
        if part["user_id"] == user_to_find:
            return part
    return None


def create_text_to_participants(color, participants: List[Participant], context: CallbackContext):
    emoji_check = "\U00002705"
    emoji_cross = "\U0000274C"
    emoji_thinks = "\U0001F4AD"

    text_message = "Test, don't worry - be happy ^_^ \n"

    text_message += f"\nThere is a match on color: \"{color}\" with ->"
    for participant in participants:
        user_chat = context.bot.get_chat(participant["user_id"])
        text_message += "\n"
        ready = participant["ready"]
        if ready is None:
            text_message += emoji_thinks
        elif ready:
            text_message += emoji_check
        else:
            text_message += emoji_cross

        if user_chat.first_name != "":
            text_message += f"{user_chat.first_name} "
        if user_chat.last_name != "":
            text_message += f"{user_chat.last_name} "

        text_message += f"(@{user_chat.username})"
    return text_message


def send_other_participants(main_user_id, color, users_group, send_user_id, context: CallbackContext):
    text_message = create_text_to_participants(color, users_group, context)

    message = context.bot.send_message(chat_id=send_user_id, text=text_message,
                                       reply_markup=create_yes_no_keyboard(main_user_id))

    group = find_group_by_main_user(groups_washing, main_user_id)

    if not group:
        return

    group["sent_messages"].append(
        {"chat_id": send_user_id, "message_id": message.message_id})


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
