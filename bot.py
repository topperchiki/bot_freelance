from telebot import types
import telebot
import work_with_files as wwf
from constants import *
import messages as mes
import random
import time
import re
from threading import Thread
tb = telebot.TeleBot(TOKEN)


@tb.message_handler(commands=['start', 'help'])
def upper(message: telebot.types.Message):
    if message.chat.type != 'private':
        return

    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ", time.gmtime(time.time() + UTC_SHIFT)) + str(message.chat.id) + " " + message.text)
        f.write("\n")

    user_id = str(message.chat.id)
    users_table = wwf.load_table(P_USERS)
    if not user_id in users_table:
        del users_table
        try:
            add_user(message.chat.id)
        except Exception as ex:
            print(ex.__class__.__name__)
    users_table = wwf.load_table(P_USERS)
    if users_table[user_id]["condition"] == 29:
        mes.error_message(message, "Закончите редактирование")
        return
    users_table[user_id]["condition"] = 0
    users_table[user_id]["type_of_ap"] = ''
    users_table[user_id]["customer_post"] = {}
    users_table[user_id]["freelance_post"] = {}
    users_table[user_id]["editing_freelance_post"] = {}
    users_table[user_id]["editing_customer_post"] = {}
    wwf.save_table(users_table, P_USERS)
    mes.main_menu_nm(message)  # Отправка самого главного меню
    try:
        with open(P_ACTIONS, "w+") as f:
            f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ", time.gmtime(time.time() + UTC_SHIFT)) + str(message.chat.id) + " " + message.text)
    except Exception:
        return


@tb.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.message.chat.type != "private":
        if call.message.chat.id not in ALLOWED_GROUP_CHATS:
            return

    user_id = str(call.message.chat.id)
    #  Если пользователя нет в базе, то добавляем
    users_table = wwf.load_table(P_USERS)
    if user_id not in users_table:
        try:
            add_user(call.message.chat.id)
        except Exception as ex:
            print(ex.__class__.__name__)

    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ", time.gmtime(time.time() + UTC_SHIFT)) + str(call.message.chat.id) + " " + call.data)
        f.write("\n")

    users_table = wwf.load_table(P_USERS)
    call_data_lowered = call.data.lower()
    if call_data_lowered == "noanswer":
        return

    elif call_data_lowered == "mainmenu":
        mes.main_menu(call.message)
        return

    elif call_data_lowered == "sidemenu":
        possible_come_from = {1, 4, 100}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.side_menu(call.message)
        return

    elif call_data_lowered == "paidservices":
        possible_come_from = {1, 75}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.paid_service_menu(call.message)
        return

    elif call_data_lowered == "createfreelancerpost":
        possible_come_from = {2, 4}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        create_temp_freelance_post(call.message.chat.id)
        mes.categories_post(call.message)
        return

    elif call.data[:12].lower() == "category_fr:":
        possible_come_from = {4, 5}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        category_id = call.data[12:]
        categories_r_table = wwf.load_table(P_CATEGORIES_R)

        # Проверяем, существует ли категория
        if category_id not in categories_r_table:
            return

        if len(categories_r_table[category_id]["children"]) > 0:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["freelance_post"]["categories"].append(category_id)
            wwf.save_table(users_table, P_USERS)

            mes.subcategories_post(call.message, category_id)
            return

        # Добавляем категорию к посту
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["freelance_post"]["categories"].append(category_id)
        # Устанавливаем шаг, на котором находимся
        wwf.save_table(users_table, P_USERS)

        # Создаем информативную кнопку
        categories_info = wwf.load_table(P_CATEGORIES)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text=categories_info[category_id]["name"] + " ✅", callback_data="noAnswer"))

        # Удаляем предыдущую клавиатуру
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.set_title_freelance_post_nm(call.message)
        return

    elif call.data[:17].lower() == "category_back_fr:":
        possible_come_from = {4}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        category_id = call.data[17:]
        categories_r_table = wwf.load_table(P_CATEGORIES_R)
        if category_id not in categories_r_table:
            return

        users_table = wwf.load_table(P_USERS)
        cat = users_table[user_id]["freelance_post"]["categories"]
        if len(cat) == 1:
            users_table[user_id]["freelance_post"]["categories"] = cat[:len(cat) - 1]
            mes.categories_post(call.message)
        elif len(cat) == 0:
            mes.side_menu(call.message)
        else:
            users_table[user_id]["freelance_post"]["categories"] = cat[:len(cat) - 1]
            mes.subcategories_post(call.message, users_table[user_id]["freelance_post"]["categories"][-1])
        wwf.save_table(users_table, P_USERS)
        return

    elif call.data[:16].lower() == "payment_type_fr:":
        possible_come_from = {10}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        pay_type = call.data[16:]
        try:
            pay_type = int(pay_type)
        except ValueError:
            return

        if pay_type < 1 or pay_type > 3:
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["freelance_post"]["payment_type"] = pay_type
        if pay_type == 1:

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Договорная ✅", callback_data="noAnswer"))
            # Удаляем предыдущую клавиатуру
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            wwf.save_table(users_table, P_USERS)

            mes.is_guarantee_necessary_freelance_nm(call.message)
            return
        elif pay_type == 2:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированная ✅", callback_data="noAnswer"))
            # Удаляем предыдущую клавиатуру
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            wwf.save_table(users_table, P_USERS)

            mes.set_fixed_price_freelance_nm(call.message)
        elif pay_type == 3:
            users_table[user_id]["freelance_post"]["price"] = [0, 0]
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Диапозон ✅", callback_data="noAnswer"))
            # Удаляем предыдущую клавиатуру
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            wwf.save_table(users_table, P_USERS)

            mes.set_range_price_1_freelance_nm(call.message)

        return

    elif call.data[:13].lower() == "guarantee_fr:":
        possible_come_from = {14}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        ans = call.data[13:]
        try:
            ans = int(ans)
        except ValueError:
            return

        if ans != 1 and ans != 0:
            return

        ans = bool(ans)
        users_table = wwf.load_table(P_USERS)
        if ans:
            users_table[user_id]["freelance_post"]["guarantee"] = True
        else:
            users_table[user_id]["freelance_post"]["guarantee"] = False
        wwf.save_table(users_table, P_USERS)
        mes.preview_post_freelance_nm(call.message, users_table[user_id]["freelance_post"])
        return

    elif call_data_lowered == "no_portfolio_fr":
        possible_come_from = {8}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["freelance_post"]["portfolio"] = ""
        wwf.save_table(users_table, P_USERS)

        mes.set_contacts_freelance_post_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_menu_fr":
        possible_come_from = [15, 17, 18, 19, 20, 21, 22, 30, 32]
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_menu_freelance(call.message)
        return

    elif call_data_lowered[:23] == "edit_pbp_categories_fr:":
        possible_come_from = [31, 32]
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        cat_id = call.data[23:]
        cat_r_table = wwf.load_table(P_CATEGORIES_R)
        users_table = wwf.load_table(P_USERS)
        if cat_id not in cat_r_table:
            return
        if cat_id != "1":
            users_table[user_id]["editing_freelance_post"]["categories"].append(cat_id)
        else:
            users_table[user_id]["editing_freelance_post"]["categories"] = []
        if len(cat_r_table[cat_id]["children"]) == 0:
            users_table[user_id]["freelance_post"]["categories"] = users_table[user_id]["editing_freelance_post"]["categories"]
            users_table[user_id]["editing_freelance_post"]["categories"] = []
            wwf.save_table(users_table, P_USERS)

            cat_table = wwf.load_table(P_CATEGORIES)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text=("..." if len(users_table[user_id]["freelance_post"]) else "") + cat_table[cat_id]["name"] + "✅", callback_data="noAnswer"))

            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

            mes.preview_post_freelance_nm(call.message, users_table[user_id]["freelance_post"])
            return
        wwf.save_table(users_table, P_USERS)
        mes.edit_pbp_categories(call.message, cat_id)
        return

    elif call_data_lowered[:25] == "edit_pbp_categories_b_fr:":
        possible_come_from = [32]
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        cat_id = call.data[25:]

        if cat_id == "0":
            mes.edit_pbp_menu_freelance(call.message)
            return

        cat_r_table = wwf.load_table(P_CATEGORIES_R)
        users_table = wwf.load_table(P_USERS)
        if cat_id not in cat_r_table:
            return

        ca = users_table[user_id]["editing_freelance_post"]["categories"]
        users_table[user_id]["editing_freelance_post"]["categories"] = ca[:len(ca) - 1]
        wwf.save_table(users_table, P_USERS)
        mes.edit_pbp_categories(call.message, cat_id)

        wwf.save_table(users_table, P_USERS)
        return

    elif call_data_lowered == "edit_pbp_title_fr":
        possible_come_from = [31]
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Название ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_title_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_description_fr":
        possible_come_from = {31}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Описание ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_description_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_memo_fr":
        possible_come_from = {31}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Памятку ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_memo_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_portfolio_fr":
        possible_come_from = {31}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Портфолио ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_portfolio_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_no_portfolio_fr":
        possible_come_from = {30}
        if users_table[user_id]["condition"] not in possible_come_from:
            return

        users_table[user_id]["freelance_post"]["portfolio"] = None
        wwf.save_table(users_table, P_USERS)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Удалено ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.preview_post_freelance_nm(call.message, users_table[user_id]["freelance_post"], True)
        mes.edit_pbp_menu_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_contacts_fr":
        possible_come_from = {31}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Контакты ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_contacts_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_payment_fr":
        possible_come_from = {31, 23, 27, 28}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_payment_freelance(call.message)
        return

    elif call_data_lowered == "edit_pbp_payment_type_fr":
        possible_come_from = {22, 24, 25}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_payment_type_freelance(call.message)
        return

    elif call_data_lowered[:27] == "edit_pbp_payment_type_2_fr:":
        possible_come_from = {23}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        pay_type = call.data[27:]

        try:
            pay_type = int(pay_type)
        except ValueError:
            return

        if pay_type == 1:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["freelance_post"]["payment_type"] = 1
            wwf.save_table(users_table, P_USERS)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Договорная ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.preview_post_freelance_nm(call.message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(call.message)
            return

        elif pay_type == 2:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["editing_freelance_post"] = {}
            users_table[user_id]["editing_freelance_post"]["payment_type"] = 2
            users_table[user_id]["editing_freelance_post"]["price"] = 0
            wwf.save_table(users_table, P_USERS)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированная ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.edit_pbp_nt_fixed_price_freelance_nm(call.message)
            return

        elif pay_type == 3:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["editing_freelance_post"] = {}
            users_table[user_id]["editing_freelance_post"]["payment_type"] = 3
            users_table[user_id]["editing_freelance_post"]["price"] = [0, 0]
            wwf.save_table(users_table, P_USERS)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Диапозон ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.edit_pbp_nt_1_price_freelance_nm(call.message)
            return

    elif call_data_lowered == "edit_pbp_price_fr":
        possible_come_from = {22}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированную цену ✅", callback_data="noAnswer"))
        tb.edit_message_text(text="Изменить", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_fixed_price_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_price_2_fr":
        possible_come_from = {22}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Изменить диапозон ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_price_1_freelance_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_guarantee_fr":
        possible_come_from = {31}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_guarantee_freelance(call.message)
        return

    elif call_data_lowered == "edit_pbp_guarantee_yes_fr":
        possible_come_from = {30}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["freelance_post"]["guarantee"] = True
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.preview_post_freelance_nm(call.message, users_table[user_id]["freelance_post"])
        return

    elif call_data_lowered == "edit_pbp_guarantee_no_fr":
        possible_come_from = {30}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["freelance_post"]["guarantee"] = False
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ❌", callback_data="noAnswer"))

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.preview_post_freelance_nm(call.message, users_table[user_id]["freelance_post"])
        return

    elif call_data_lowered == "preview_post_fr":
        possible_come_from = {31, 14}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.preview_post_mini(call.message)
        return

    elif call_data_lowered == "post_fr":
        possible_come_from = {15}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        if users_table[user_id]["condition"] != 15:
            return
        posts_table = wwf.load_table(P_POSTS)
        ownership_table = wwf.load_table(P_OWNERSHIPS)
        new_id = random.randint(100000, 999999)
        while new_id in posts_table:
            new_id = random.randint(100000, 999999)

        new_id = str(new_id)
        users_table[user_id]["freelance_post"]["post_id"] = new_id
        wwf.save_table(users_table, P_USERS)

        ans = mes.post_nm(ID_POST_CHANNEL, users_table[user_id]["freelance_post"])
        posts_table[new_id] = users_table[user_id]["freelance_post"]
        posts_table[new_id]["time_published"] = time.time()
        posts_table[new_id]["time_upped"] = posts_table[new_id]["time_published"]
        ownership_table[user_id].append(new_id)
        wwf.save_table(ownership_table, P_OWNERSHIPS)

        posts_table[new_id]["published"] = True

        wwf.save_table(posts_table, P_POSTS)
        dposts_table = wwf.load_table(P_D_POSTS)
        t = posts_table[new_id]["time_published"] + 169200
        if t in dposts_table:
            dposts_table[t].append({"cid": ID_POST_CHANNEL, "mid": ans.message_id, "replace": 0})
        else:
            dposts_table[t] = [{"cid": ID_POST_CHANNEL, "mid": ans.message_id, "replace": 0}]
        wwf.save_table(dposts_table, P_D_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Опубликовано ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.posted(call.message, new_id)
        return

    elif call_data_lowered == "verification":
        possible_come_from = {3}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Верификация ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        users_table = wwf.load_table(P_USERS)
        if users_table[user_id]["verification_request_was_sent"] != -1:
            mes.show_verification_request(call.message, users_table[user_id])
            return

        mes.write_about_yourself_ver_nm(call.message)
        return

    elif call_data_lowered == "payverification":
        possible_come_from = {77}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        if users_table[user_id]["verification_request_was_sent"] != -1:
            return

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.buy_verification(call.message)
        return

    elif call_data_lowered[:14] == "buyingupsmenu:":
        order_table = wwf.load_table(P_ORDERS)
        order_table[user_id] =  {'post_id': '', 'type': '', 'number': '', "mode": ''}
        wwf.save_table(order_table, P_ORDERS)
        mes.buying_ups_menu(call.message, call.data[14:])
        return

    elif call_data_lowered[:14] == "buyingautoups:":
        possible_come_from = {70, 71}
        if users_table[user_id]["condition"] not in possible_come_from:
            return

        post_id = call.data[14:]
        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] == post_id:
            return
        else:
            orders_table = wwf.load_table(P_ORDERS)
            orders_table[user_id]["type"] = 'ap'
            orders_table[user_id]["post_id"] = post_id
            wwf.save_table(orders_table, P_ORDERS)

            mes.buying_auto_ups_menu(call.message, post_id)
            return

    elif call_data_lowered[:18] == "buyingautoupsmode:":
        possible_come_from = {71}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mode = call.data[18]
        try:
            mode = int(mode)
        except ValueError:
            return
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton('😞', callback_data="sideMenu"))

        post_id = call.data[20:]
        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] == post_id:
            return
        if int(posts_table[post_id]['auto_ups']) != 0 and mode != int(posts_table[post_id]['auto_ups_type']):
            a = tb.send_message(call.message.chat.id,'Вы уже купили автоподьёмы для данного объявления. Через 24 часа спустя последнее автоподнятие вы можете купить их снова',
                                reply_markup=keyboard)
        else:
            orders_table = wwf.load_table(P_ORDERS)
            orders_table[user_id]["mode"] = mode
            wwf.save_table(orders_table, P_ORDERS)

            mes.enter_auto_ups_count_buying_nm(call.message, post_id)
            return

    elif call_data_lowered[:16] == "buyingmanualups:":
        possible_come_from = {70}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[16:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] == post_id:
            return

        orders_table = wwf.load_table(P_ORDERS)
        orders_table[user_id]["type"] = 'hand'
        orders_table[user_id]["post_id"] = post_id
        wwf.save_table(orders_table, P_ORDERS)

        mes.buying_manual_ups_menu_nm(call.message, post_id)
        return

    elif call_data_lowered[:8] == "getpost:":
        post_id = call.data[8:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != user_id:
            return

        mes.send_post(call.message, post_id)
        return

    elif call_data_lowered == "createcustomerpost":
        possible_come_from = {2}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        create_temp_customer_post(call.message.chat.id)
        mes.categories_post(call.message, True)
        return

    elif call.data[:12].lower() == "category_cu:":
        possible_come_from = {100, 101}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        category_id = call.data[12:]
        categories_r_table = wwf.load_table(P_CATEGORIES_R)

        # Проверяем, существует ли категория
        if category_id not in categories_r_table:
            return

        if len(categories_r_table[category_id]["children"]) > 0:
            users_table[user_id]["customer_post"]["categories"].append(category_id)
            wwf.save_table(users_table, P_USERS)

            mes.subcategories_post(call.message, category_id, True)
            return

        # Добавляем категорию к посту
        users_table[user_id]["customer_post"]["categories"].append(category_id)
        # Устанавливаем шаг, на котором находимся
        wwf.save_table(users_table, P_USERS)

        # Создаем информативную кнопку
        categories_info = wwf.load_table(P_CATEGORIES)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text=categories_info[category_id]["name"] + " ✅", callback_data="noAnswer"))

        # Удаляем предыдущую клавиатуру
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.set_title_customer_post_nm(call.message)
        return

    elif call.data[:17].lower() == "category_back_cu:":
        possible_come_from = {100, 101}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        category_id = call.data[17:]
        categories_r_table = wwf.load_table(P_CATEGORIES_R)
        if category_id not in categories_r_table:
            return

        users_table = wwf.load_table(P_USERS)
        cat = users_table[user_id]["customer_post"]["categories"]
        if len(cat) == 1:
            users_table[user_id]["customer_post"]["categories"] = cat[:len(cat) - 1]
            mes.categories_post(call.message, True)
        elif len(cat) == 0:
            mes.side_menu(call.message)
        else:
            users_table[user_id]["customer_post"]["categories"] = cat[:len(cat) - 1]
            mes.subcategories_post(call.message, users_table[user_id]["customer_post"]["categories"][-1], True)
        wwf.save_table(users_table, P_USERS)
        return

    elif call_data_lowered[:13] == "portfolio_cu:":
        possible_come_from = {103}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        p_flag = call.data[13:]
        try:
            p_flag = int(p_flag)
        except ValueError:
            return

        users_table = wwf.load_table(P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        if p_flag == 1:
            users_table[user_id]["customer_post"]["portfolio"] = True
            keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))
        elif p_flag == 0:
            users_table[user_id]["customer_post"]["portfolio"] = False
            keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ❌", callback_data="noAnswer"))
        wwf.save_table(users_table, P_USERS)

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.set_contacts_customer_post_nm(call.message)
        return

    elif call.data[:16].lower() == "payment_type_cu:":
        possible_come_from = {105}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        pay_type = call.data[16:]
        try:
            pay_type = int(pay_type)
        except ValueError:
            return

        if pay_type < 1 or pay_type > 3:
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["customer_post"]["payment_type"] = pay_type
        if pay_type == 1:

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Договорная ✅", callback_data="noAnswer"))
            # Удаляем предыдущую клавиатуру
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            wwf.save_table(users_table, P_USERS)

            mes.is_guarantee_necessary_customer_nm(call.message)
            return
        elif pay_type == 2:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированная ✅", callback_data="noAnswer"))
            # Удаляем предыдущую клавиатуру
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            wwf.save_table(users_table, P_USERS)

            mes.set_fixed_price_customer_nm(call.message)
        elif pay_type == 3:
            users_table[user_id]["customer_post"]["price"] = [0, 0]
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Диапозон ✅", callback_data="noAnswer"))
            # Удаляем предыдущую клавиатуру
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            wwf.save_table(users_table, P_USERS)

            mes.set_range_price_1_customer_nm(call.message)

        return

    elif call_data_lowered[:13] == "guarantee_cu:":
        possible_come_from = {109}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        g_flag = call.data[13:]
        try:
            g_flag = int(g_flag)
        except ValueError:
            return

        users_table = wwf.load_table(P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        if g_flag == 1:
            users_table[user_id]["customer_post"]["guarantee"] = True
            keyboard.add(telebot.types.InlineKeyboardButton(text="Да ", callback_data="noAnswer"))
        else:
            users_table[user_id]["customer_post"]["guarantee"] = False
            keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ", callback_data="noAnswer"))
        wwf.save_table(users_table, P_USERS)

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.preview_post_customer_nm(call.message, users_table[user_id]["customer_post"])
        return

    elif call_data_lowered == "post_cu":
        possible_come_from = {110}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        if users_table[user_id]["condition"] != 110:
            return
        posts_table = wwf.load_table(P_POSTS)
        ownership_table = wwf.load_table(P_OWNERSHIPS)
        new_id = random.randint(100000, 999999)
        while new_id in posts_table:
            new_id = random.randint(100000, 999999)
        new_id = str(new_id)

        users_table[user_id]["customer_post"]["post_id"] = new_id
        wwf.save_table(users_table, P_USERS)

        ans = mes.post_nm(ID_POST_CHANNEL, users_table[user_id]["customer_post"])
        posts_table[new_id] = users_table[user_id]["customer_post"]
        posts_table[new_id]["time_published"] = time.time()
        posts_table[new_id]["time_upped"] = posts_table[new_id]["time_published"]
        ownership_table[user_id].append(new_id)
        wwf.save_table(ownership_table, P_OWNERSHIPS)

        posts_table[new_id]["published"] = True

        wwf.save_table(posts_table, P_POSTS)
        dposts_table = wwf.load_table(P_D_POSTS)
        t = posts_table[new_id]["time_published"] + 169200
        if t in dposts_table:
            dposts_table[t].append({"cid": ID_POST_CHANNEL, "mid": ans.message_id, "replace": 0})
        else:
            dposts_table[t] = [{"cid": ID_POST_CHANNEL, "mid": ans.message_id, "replace": 0}]
        wwf.save_table(dposts_table, P_D_POSTS)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Опубликовано ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.posted(call.message, new_id)
        return

    elif call_data_lowered == "edit_pbp_menu_cu":
        possible_come_from = {110, 111, 125, 112, 113, 114, 115, 123}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_menu_customer(call.message)

    elif call_data_lowered[:23] == "edit_pbp_categories_cu:":
        possible_come_from = {124, 125}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        cat_id = call.data[23:]
        cat_r_table = wwf.load_table(P_CATEGORIES_R)
        users_table = wwf.load_table(P_USERS)
        if cat_id not in cat_r_table:
            return
        if cat_id != "1":
            users_table[user_id]["editing_customer_post"]["categories"].append(cat_id)
        else:
            users_table[user_id]["editing_customer_post"]["categories"] = []
        if len(cat_r_table[cat_id]["children"]) == 0:
            users_table[user_id]["customer_post"]["categories"] = users_table[user_id]["editing_customer_post"]["categories"]
            users_table[user_id]["editing_customer_post"]["categories"] = []
            wwf.save_table(users_table, P_USERS)

            cat_table = wwf.load_table(P_CATEGORIES)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text=("..." if len(users_table[user_id]["customer_post"]) else "") + cat_table[cat_id]["name"] + "✅", callback_data="noAnswer"))

            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

            mes.preview_post_customer_nm(call.message, users_table[user_id]["customer_post"])
            return
        wwf.save_table(users_table, P_USERS)
        mes.edit_pbp_categories(call.message, cat_id, True)
        return

    elif call_data_lowered[:25] == "edit_pbp_categories_b_cu:":
        possible_come_from = {124, 125}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        cat_id = call.data[25:]

        if cat_id == "0":
            mes.edit_pbp_menu_customer(call.message)
            return

        cat_r_table = wwf.load_table(P_CATEGORIES_R)
        users_table = wwf.load_table(P_USERS)
        if cat_id not in cat_r_table:
            return
        ca = users_table[user_id]["editing_customer_post"]["categories"]
        users_table[user_id]["editing_customer_post"]["categories"] = ca[:len(ca) - 1]
        wwf.save_table(users_table, P_USERS)
        mes.edit_pbp_categories(call.message, cat_id, True)
        return

    elif call_data_lowered == "edit_pbp_title_cu":
        possible_come_from = {124}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Название ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_title_customer_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_description_cu":
        possible_come_from = {124}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Описание ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_description_customer_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_portfolio_cu":
        possible_come_from = {124}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Портфолио ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_portfolio_customer_nm(call.message)
        return

    elif call_data_lowered[:24] == "edit_pbp_portfolio_1_cu:":
        possible_come_from = {113}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        p_flag = call.data[24:]
        try:
            p_flag = int(p_flag)
        except ValueError:
            return

        users_table = wwf.load_table(P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        if p_flag == 1:
            users_table[user_id]["customer_post"]["portfolio"] = True
            keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))
        elif p_flag == 0:
            users_table[user_id]["customer_post"]["portfolio"] = False
            keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ❌", callback_data="noAnswer"))
        wwf.save_table(users_table, P_USERS)

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.preview_post_customer_nm(call.message, users_table[user_id]["customer_post"], True)
        mes.edit_pbp_menu_customer_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_contacts_cu":
        possible_come_from = {124}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Контакты ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_contacts_customer_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_payment_cu":
        possible_come_from = {124, 116, 120, 121}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_payment_customer(call.message)
        return

    elif call_data_lowered == "edit_pbp_payment_type_cu":
        possible_come_from = {115, 117, 118}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_payment_type_customer(call.message)
        return

    elif call_data_lowered[:27] == "edit_pbp_payment_type_2_cu:":
        possible_come_from = {116}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        pay_type = call.data[27:]

        try:
            pay_type = int(pay_type)
        except ValueError:
            return

        if pay_type == 1:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["customer_post"]["payment_type"] = 1
            wwf.save_table(users_table, P_USERS)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Договорная ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.preview_post_customer_nm(call.message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(call.message)
            return

        elif pay_type == 2:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["editing_customer_post"] = {}
            users_table[user_id]["editing_customer_post"]["payment_type"] = 2
            users_table[user_id]["editing_customer_post"]["price"] = 0
            wwf.save_table(users_table, P_USERS)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированная ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.edit_pbp_nt_fixed_price_customer_nm(call.message)
            return

        elif pay_type == 3:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]["editing_customer_post"] = {}
            users_table[user_id]["editing_customer_post"]["payment_type"] = 3
            users_table[user_id]["editing_customer_post"]["price"] = [0, 0]
            wwf.save_table(users_table, P_USERS)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Диапозон ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.edit_pbp_nt_1_price_customer_nm(call.message)
            return

    elif call_data_lowered == "edit_pbp_price_cu":
        possible_come_from = {116}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированную цену ✅", callback_data="noAnswer"))
        tb.edit_message_text(text="Изменить", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_fixed_price_customer_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_price_2_cu":
        possible_come_from = {116}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Изменить диапозон ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_pbp_price_1_customer_nm(call.message)
        return

    elif call_data_lowered == "edit_pbp_guarantee_cu":
        possible_come_from = {124}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.edit_pbp_guarantee_customer(call.message)
        return

    elif call_data_lowered == "edit_pbp_guarantee_yes_cu":
        possible_come_from = {123}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["customer_post"]["guarantee"] = True
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.preview_post_customer_nm(call.message, users_table[user_id]["customer_post"])
        return

    elif call_data_lowered == "edit_pbp_guarantee_no_cu":
        possible_come_from = {123}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["customer_post"]["guarantee"] = False
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ❌", callback_data="noAnswer"))

        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.preview_post_customer_nm(call.message, users_table[user_id]["customer_post"])
        return

    elif call_data_lowered == "preview_post_cu":
        possible_come_from = {124, 109}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        mes.preview_post_mini(call.message, True)
        return

    elif call_data_lowered[:5] == "edit:":
        post_id = call.data[5:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        mes.edit_post_menu(call.message, post_id)
        return

    elif call_data_lowered[:11] == "edit_title:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[11:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != user_id:
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Название ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.edit_title_nm(call.message)
        return

    elif call_data_lowered[:19] == "edit_guarantee_yes:":
        possible_come_from = {88}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[19:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        posts_table[post_id]["guarantee"] = True
        wwf.save_table(posts_table, P_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.send_post_nm(call.message, post_id)
        return

    elif call_data_lowered[:18] == "edit_guarantee_no:":
        possible_come_from = {88}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[18:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        posts_table[post_id]["guarantee"] = False
        wwf.save_table(posts_table, P_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.send_post_nm(call.message, post_id)
        return

    elif call_data_lowered[:19] == "edit_portfolio_yes:":
        possible_come_from = {87}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[19:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        posts_table[post_id]["portfolio"] = True
        wwf.save_table(posts_table, P_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.send_post_nm(call.message, post_id)
        return

    elif call_data_lowered[:18] == "edit_portfolio_no:":
        possible_come_from = {87}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[18:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        posts_table[post_id]["portfolio"] = False
        wwf.save_table(posts_table, P_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.send_post_nm(call.message, post_id)
        return

    elif call_data_lowered[:17] == "edit_description:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[17:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Описание ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.edit_description_nm(call.message)
        return

    elif call_data_lowered[:10] == "edit_memo:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[10:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Памятку ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.edit_memo_nm(call.message)
        return

    elif call_data_lowered[:15] == "edit_portfolio:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[15:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        if posts_table[post_id]["type"] == 1:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Портфолио ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            mes.edit_portfolio_fr_nm(call.message, post_id)
        elif posts_table[post_id]["type"] == 2:
            mes.edit_portfolio_cu(call.message, post_id)
        return

    elif call_data_lowered[:15] == "edit_guarantee:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[15:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        mes.edit_guarantee(call.message, post_id)
        return

    elif call_data_lowered[:14] == "edit_contacts:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[14:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Контакты ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.edit_contacts_nm(call.message)
        return

    elif call_data_lowered[:16] == "edit_categories:":
        possible_come_from = {80}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[16:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        users_table[user_id]["editing"]["categories"] = []
        wwf.save_table(users_table, P_USERS)

        mes.edit_categories(call.message, "1")
        return

    elif call_data_lowered[:18] == "edit_categories_1:":
        possible_come_from = {"80", "81"}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        cat_id = call.data[18:]
        cat_r_table = wwf.load_table(P_CATEGORIES_R)
        users_table = wwf.load_table(P_USERS)
        if cat_id not in cat_r_table:
            return
        if cat_id != "1":
            users_table[user_id]["editing"]["categories"].append(cat_id)
        else:
            users_table[user_id]["editing"]["categories"] = []
        if len(cat_r_table[cat_id]["children"]) == 0:
            posts_table = wwf.load_table(P_POSTS)
            posts_table[users_table[user_id]["editing"]["post_id"]]["categories"] = users_table[user_id]["editing"]["categories"]
            users_table[user_id]["editing"]["categories"] = []
            wwf.save_table(users_table, P_USERS)
            wwf.save_table(posts_table, P_POSTS)

            cat_table = wwf.load_table(P_CATEGORIES)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text=("..." if len(posts_table[users_table[user_id]["editing"]["post_id"]]["categories"]) else "") + cat_table[cat_id]["name"] + "✅", callback_data="noAnswer"))

            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

            mes.send_post_nm(call.message, users_table[user_id]["editing"]["post_id"])
            return

        wwf.save_table(users_table, P_USERS)
        mes.edit_categories(call.message, cat_id)
        return

    elif call_data_lowered[:18] == "edit_categories_b:":
        possible_come_from = {81}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        cat_id = call.data[18:]

        if cat_id == "0":
            users_table = wwf.load_table(P_USERS)
            mes.edit_post_menu(call.message, users_table["editing"]["post_id"])
            return

        cat_r_table = wwf.load_table(P_CATEGORIES_R)
        users_table = wwf.load_table(P_USERS)
        if cat_id not in cat_r_table:
            return

        ca = users_table[user_id]["editing"]["categories"]
        users_table[user_id]["editing"]["categories"] = ca[:len(ca) - 1]
        wwf.save_table(users_table, P_USERS)
        mes.edit_pbp_categories(call.message, cat_id)

        wwf.save_table(users_table, P_USERS)
        return

    elif call_data_lowered[:22] == "edit_portfolio_delete:":
        possible_come_from = {86}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[22:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        posts_table[post_id]["portfolio"] = ""
        wwf.save_table(posts_table, P_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Удалено ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.send_post_nm(call.message, post_id)
        return

    elif call_data_lowered[:15] == "edit_pay_type1:":
        possible_come_from = {89}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[15:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        posts_table[post_id]["payment_type"] = 1
        wwf.save_table(posts_table, P_POSTS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Договорная ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.send_post_nm(call.message, post_id)
        return

    elif call_data_lowered[:15] == "edit_pay_type2:":
        possible_come_from = {89}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[15:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        users_table[user_id]["editing"]["payment_type"] = 2
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированная ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.edit_fixed_price_nm(call.message)
        return

    elif call_data_lowered[:15] == "edit_pay_type3:":
        possible_come_from = {89}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[15:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        users_table[user_id]["editing"]["payment_type"] = 3
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Диапозон ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.edit_price_1_nm(call.message)
        return

    elif call_data_lowered[:13] == "edit_payment:":
        possible_come_from = {80, 90, 91}
        if users_table[user_id]["condition"] not in possible_come_from:
            return
        post_id = call.data[13:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != user_id:
            return

        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["editing"]["post_id"] = post_id
        wwf.save_table(users_table, P_USERS)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Оплату ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        mes.edit_pay_nm(call.message, post_id)
        return

    elif call_data_lowered[:3] == "up:":
        post_id = call.data[3:]

        posts_table = wwf.load_table(P_POSTS)
        if post_id not in posts_table or posts_table[post_id]["owner_id"] != str(call.message.chat.id):
            return

        if users_table[user_id]["manual_ups"] == 0:
            mes.error_message(call.message, "Сначала купите ручные подъемы для этого объявления")
            return

        dif = min(max(time.time() - posts_table[post_id]["time_upped"], 0), 10800)
        if dif < 10800:
            next_possible_up_time = 10800 - dif
            mes.error_message(call.message, "Ручной подъем можно делать не чаще 1 раза в 3 часа. До следующего подъема осталось: " + str(int(next_possible_up_time / 3600)) + ":" + str(int((next_possible_up_time % 3600) / 60)) + ":" + str(int((next_possible_up_time % 60))))
            return

        users_table[user_id]["manual_ups"] -= 1
        wwf.save_table(users_table, P_USERS)
        posts_table[post_id]["time_upped"] = time.time()
        wwf.save_table(posts_table, P_POSTS)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text="Поднять ✅", callback_data="noAnswer"))
        tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
        mes.post_nm(ID_POST_CHANNEL, posts_table[post_id])
        mes.error_message(call.message, "Поднято")
        return

    elif call_data_lowered[:7] == "report:":
        post_id = call_data_lowered[7:]

        posts_table = wwf.load_table(P_POSTS)
        if (post_id not in posts_table) or (call.from_user.id in posts_table[post_id]["users_reported"]):
            return

        posts_table[post_id]["reported"] += 1
        posts_table[post_id]["users_reported"].append(call.from_user.id)
        if not posts_table[post_id]["report_was_sent"] and is_need_to_delete(posts_table[post_id]):
            posts_table[post_id]["report_was_sent"] = True
            wwf.save_table(posts_table, P_POSTS)
            mes.send_report_nm(call.message, ID_MANAGE_CHANNEL)
            return
        wwf.save_table(posts_table, P_POSTS)
        mes.report_was_sent(call.from_user.id)
        return

    elif call_data_lowered[:7] == "verify:":
        user_id = call_data_lowered[7:]

        users_table = wwf.load_table(P_USERS)

        users_table[user_id]["verification_request_was_sent"] = -1
        users_table[user_id]["verified"] = True
        wwf.save_table(users_table, P_USERS)
        mes.edit_verification_status(call.message, user_id, True)
        return

    elif call_data_lowered[:9] == "unverify:":
        user_id = call_data_lowered[9:]

        users_table = wwf.load_table(P_USERS)

        users_table[user_id]["verification_request_was_sent"] = -1
        users_table[user_id]["verified"] = False
        wwf.save_table(users_table, P_USERS)
        mes.edit_verification_status(call.message, user_id, False)
        return

    elif call_data_lowered[:12] == "delete_post:":
        message_id = call_data_lowered[12:]

        if call.message.chat.id == ID_MANAGE_CHANNEL:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Удалено ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

            tb.delete_message(chat_id=ID_POST_CHANNEL, message_id=message_id)
            return

    elif call_data_lowered[:14] == "nodelete_post:":
        message_id = call_data_lowered[14:]

        if call.message.chat.id == ID_MANAGE_CHANNEL:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text="Не удалено ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
            return
    # Проверка на установленный код
    try:
        code = int(call.data)

    except ValueError:
        return

    if 2000 > code > 1000:
        page = code - 1000
        mes.send_posts_page(call.message, page)
        return


@tb.message_handler()
def common_message_handler(message: telebot.types.Message):
    if message.chat.type != 'private':
        return

    user_id = str(message.chat.id)
    #  Если пользователя нет в базе, то добавляем
    users_table = wwf.load_table(P_USERS)
    if user_id not in users_table:
        del users_table
        try:
            add_user(message.chat.id)
        except Exception as ex:
            print(ex.__class__.__name__)

    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ", time.gmtime(time.time() + UTC_SHIFT)) + str(message.chat.id) + " " + message.text)
        f.write("\n")

    if len(message.text) > 8 and message.text[:8].lower() == "/id_post" and message.text[8:].lower() != "число":
        post_id = message.text[8:]

        mes.send_post_nm(message, post_id)
        return

    elif message.text.lower() == "назад":
        users_table = wwf.load_table(P_USERS)
        user = users_table[user_id]
        step = user["condition"]
        if step != 0:
            if step == 1:
                return

            elif step == 2:
                return

            elif step == 3:
                return

            elif step == 4:
                return

            elif step == 5:
                users_table[user_id]["freelance_post"]["categories"] = users_table[user_id]["freelance_post"]["categories"][:-1]
                wwf.save_table(users_table, P_USERS)
                if len(users_table[user_id]["freelance_post"]["categories"]) == 0:
                    mes.categories_post_nm(message)

                else:
                    mes.subcategories_post_nm(message, users_table[user_id]["freelance_post"]["categories"][-1])
                return

            elif step == 6:
                mes.set_title_freelance_post_nm(message)
                return

            elif step == 7:
                mes.set_description_freelance_post_nm(message)
                return

            elif step == 8:
                mes.set_memo_freelance_post_nm(message)
                return

            elif step == 9:
                mes.set_portfolio_freelance_post_nm(message)
                return

            elif step == 10:
                mes.set_contacts_freelance_post_nm(message)
                return

            elif step == 11:
                mes.set_payment_type_freelance_post_nm(message)
                return

            elif step == 12:
                mes.set_payment_type_freelance_post_nm(message)
                return

            elif step == 13:
                mes.set_range_price_1_freelance_nm(message)
                return

            elif step == 14:
                mes.set_payment_type_freelance_post_nm(message)
                return

            elif step == 15:
                mes.is_guarantee_necessary_freelance_nm(message)
                return

            elif step == 16:
                return

            elif step == 17:
                mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
                mes.edit_pbp_menu_freelance_nm(message)
                return

            elif step == 18:
                mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
                mes.edit_pbp_menu_freelance_nm(message)
                return

            elif step == 19:
                mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
                mes.edit_pbp_menu_freelance_nm(message)
                return

            elif step == 20:
                mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
                mes.edit_pbp_menu_freelance_nm(message)
                return

            elif step == 21:
                mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
                mes.edit_pbp_menu_freelance_nm(message)
                return

            elif step == 22:
                mes.edit_pbp_menu_freelance_nm(message)
                return

            elif step == 23:
                return

            elif step == 24:
                mes.edit_pbp_payment_type_freelance_nm(message)
                return

            elif step == 25:
                mes.edit_pbp_payment_type_freelance_nm(message)
                return

            elif step == 26:
                mes.edit_pbp_nt_1_price_freelance_nm(message)
                return

            elif step == 27:
                mes.edit_pbp_payment_freelance_nm(message)
                return

            elif step == 28:
                mes.edit_pbp_payment_freelance_nm(message)
                return

            elif step == 29:
                mes.error_message(message, "Необходимо ввести второе число")
                return

            elif step == 30:
                mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"])
                return

            elif step == 31:
                return

            elif step == 70:
                return

            elif step == 71:
                return

            elif step == 72:
                mes.buying_ups_menu_nm(message, users_table[user_id]["buying_post"])
                return

            elif step == 73:
                mes.buying_ups_menu_nm(message, users_table[user_id]["buying_post"])
                return

            elif step == 74:
                return

            elif step == 75:
                mes.paid_service_menu_nm(message)
                return

            elif step == 76:
                mes.write_about_yourself_ver_nm(message)
                return

            elif step == 77:
                mes.send_links_ver_nm(message)
                return

            elif step == 78:
                return

            elif step == 80:
                return

            elif step == 81:
                return

            elif step == 82:

                mes.edit_post_menu_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 83:
                mes.edit_post_menu_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 84:
                mes.edit_post_menu_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 85:
                mes.edit_post_menu_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 86:
                mes.edit_post_menu_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 87:
                return

            elif step == 88:
                return

            elif step == 89:
                return

            elif step == 90:
                wwf.save_table(users_table, P_USERS)
                mes.edit_pay_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 91:
                wwf.save_table(users_table, P_USERS)
                mes.edit_pay_nm(message, users_table[user_id]["editing"]["post_id"])
                return

            elif step == 92:
                wwf.save_table(users_table, P_USERS)
                mes.edit_price_1_nm(message)
                return

            elif step == 100:
                return

            elif step == 101:
                users_table[user_id]["customer_post"]["categories"] = users_table[user_id]["customer_post"]["categories"][:-1]
                wwf.save_table(users_table, P_USERS)
                if len(users_table[user_id]["customer_post"]["categories"]) == 0:
                    mes.categories_post_nm(message, True)

                else:
                    mes.subcategories_post_nm(message, users_table[user_id]["customer_post"]["categories"][-1], True)
                return

            elif step == 102:
                mes.set_title_customer_post_nm(message)
                return

            elif step == 103:
                mes.set_description_customer_post_nm(message)
                return

            elif step == 104:
                mes.set_portfolio_customer_post_nm(message)
                return

            elif step == 105:
                mes.set_contacts_customer_post_nm(message)
                return

            elif step == 106:
                mes.set_payment_type_customer_post_nm(message)
                return

            elif step == 107:
                mes.set_payment_type_customer_post_nm(message)
                return

            elif step == 108:
                mes.set_range_price_1_customer_nm(message)

            elif step == 109:
                mes.set_payment_type_customer_post_nm(message)
                return

            elif step == 110:
                mes.is_guarantee_necessary_customer_nm(message)
                return

            elif step == 111:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

            elif step == 112:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

            elif step == 113:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

            elif step == 114:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

            elif step == 115:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

            elif step == 116:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

            elif step == 117:
                mes.edit_pbp_payment_type_customer_nm(message)
                return

            elif step == 118:
                mes.edit_pbp_payment_type_freelance_nm(message)
                return

            elif step == 119:
                mes.edit_pbp_nt_1_price_freelance_nm(message)
                return

            elif step == 120:
                mes.edit_pbp_payment_type_freelance_nm(message)
                return

            elif step == 121:
                mes.edit_pbp_payment_type_freelance_nm(message)
                return

            elif step == 122:
                mes.error_message(message, "Необходимо ввести второе число")
                return

            elif step == 123:
                mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
                mes.edit_pbp_menu_customer_nm(message)
                return

    elif message.text.lower() == "в главное меню":
        users_table = wwf.load_table(P_USERS)
        if users_table[user_id]["condition"] == 29:
            mes.error_message(message, "Закончите редактирование")
            return
        users_table[user_id]["condition"] = 0
        users_table[user_id]["customer_post"] = {}
        users_table[user_id]["freelance_post"] = {}
        users_table[user_id]["editing_freelance_post"] = {}
        users_table[user_id]["editing_customer_post"] = {}
        wwf.save_table(users_table, P_USERS)
        mes.main_menu_nm(message)
        return

    else:
        users_table = wwf.load_table(P_USERS)
        step = users_table[user_id]["condition"]
        if step == 1:
            return

        elif step == 2:
            return

        elif step == 3:
            return

        elif step == 4:
            return

        elif step == 5:
            ans, error_text = is_suitable_title_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["title"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_description_freelance_post_nm(message)
            return

        elif step == 6:
            ans, error_text = is_suitable_description_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["description"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_memo_freelance_post_nm(message)
            return

        elif step == 7:
            ans, error_text = is_suitable_memo_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["memo"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_portfolio_freelance_post_nm(message)
            return

        elif step == 8:
            ans, error_text = is_url(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["portfolio"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_contacts_freelance_post_nm(message)
            return

        elif step == 9:
            ans, error_text = is_suitable_contacts_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["contacts"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_payment_type_freelance_post_nm(message)
            return

        elif step == 10:
            return

        elif step == 11:
            ans, error_text = is_suitable_price_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["price"] = float(message.text)
            wwf.save_table(users_table, P_USERS)
            mes.is_guarantee_necessary_freelance_nm(message)
            return

        elif step == 12:
            ans, error_text = is_suitable_price_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["price"][0] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.set_range_price_2_freelance_nm(message)
            return

        elif step == 13:
            ans, error_text = is_suitable_price_2_fl(message.text, int(users_table[user_id]["freelance_post"]["price"][0]))
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["price"][1] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.is_guarantee_necessary_freelance_nm(message)
            return

        elif step == 14:
            return

        elif step == 15:
            return

        elif step == 16:
            return

        elif step == 17:
            ans, error_text = is_suitable_title_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["title"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 18:
            ans, error_text = is_suitable_description_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["description"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 19:
            ans, error_text = is_suitable_memo_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["memo"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 20:
            ans, error_text = is_url(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["portfolio"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 21:
            ans, error_text = is_suitable_contacts_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["contacts"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 22:
            return

        elif step == 23:
            return

        elif step == 24:
            ans, error_text = is_suitable_price_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return
            users_table[user_id]["freelance_post"]["payment_type"] = 2
            users_table[user_id]["freelance_post"]["price"] = (int(100 * float(message.text)) / 100)
            users_table[user_id]["editing_freelance_post"] = {}
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 25:
            ans, error_text = is_suitable_price_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["editing_freelance_post"]["price"][0] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.edit_pbp_nt_2_price_freelance_nm(message)
            return

        elif step == 26:
            ans, error_text = is_suitable_price_2_fl(message.text, users_table[user_id]["editing_freelance_post"]["price"][0])
            if not ans:
                mes.error_message(message, error_text)
                return
            users_table[user_id]["freelance_post"]["payment_type"] = 3
            users_table[user_id]["freelance_post"]["price"] = [0, 0]
            users_table[user_id]["freelance_post"]["price"][0] = users_table[user_id]["editing_freelance_post"]["price"][0]
            users_table[user_id]["freelance_post"]["price"][1] = (int(100 * float(message.text)) / 100)
            users_table[user_id]["editing_freelance_post"] = {}
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 27:
            ans, error_text = is_suitable_price_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["price"] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 28:
            ans, error_text = is_suitable_price_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["price"][0] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.edit_pbp_price_2_freelance_nm(message)
            return

        elif step == 29:
            ans, error_text = is_suitable_price_2_fl(message.text, users_table[user_id]["freelance_post"]["price"][0])
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["freelance_post"]["price"][1] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_freelance_nm(message, users_table[user_id]["freelance_post"], True)
            mes.edit_pbp_menu_freelance_nm(message)
            return

        elif step == 30:
            return

        elif step == 31:
            return

        elif step == 70:
            return

        elif step == 71:
            return

        elif step == 72:
            ans, error_text = is_suitable_ups_count(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return
            mes.bill(message)
            return

        elif step == 73:
            ans, error_text = is_suitable_ups_count(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return
            mes.bill(message)
            return

        elif step == 74:
            return

        elif step == 75:
            if users_table[user_id]["verification_request_was_sent"] != -1:
                return
            ans, error_text = is_suitable_about_verification(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return
            users_table[user_id]["verification_request"]["about"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.send_links_ver_nm(message)
            return

        elif step == 76:
            if users_table[user_id]["verification_request_was_sent"] != -1:
                return
            ans, error_text = is_suitable_links_verification(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return
            users_table[user_id]["verification_request"]["links"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_verification_request_nm(message, users_table[user_id])
            return

        elif step == 77:
            return

        elif step == 78:
            return

        elif step == 80:
            return

        elif step == 81:
            return

        elif step == 82:
            posts_table = wwf.load_table(P_POSTS)
            post = posts_table[users_table[user_id]["editing"]["post_id"]]
            if post["type"] == 1:
                ans, error_text = is_suitable_title_fl(message.text)
            elif post["type"] == 2:
                ans, error_text = is_suitable_title_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["title"] = message.text
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 83:
            posts_table = wwf.load_table(P_POSTS)
            post = posts_table[users_table[user_id]["editing"]["post_id"]]
            if post["type"] == 1:
                ans, error_text = is_suitable_description_fl(message.text)
            elif post["type"] == 2:
                ans, error_text = is_suitable_description_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["description"] = message.text
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 84:
            posts_table = wwf.load_table(P_POSTS)
            ans, error_text = is_suitable_memo_fl(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["memo"] = message.text
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 85:
            posts_table = wwf.load_table(P_POSTS)
            post = posts_table[users_table[user_id]["editing"]["post_id"]]
            if post["type"] == 1:
                ans, error_text = is_suitable_contacts_fl(message.text)
            elif post["type"] == 2:
                ans, error_text = is_suitable_contacts_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["contacts"] = message.text
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 86:
            posts_table = wwf.load_table(P_POSTS)
            ans, error_text = is_url(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["portfolio"] = message.text
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 87:

            posts_table = wwf.load_table(P_POSTS)
            ans, error_text = is_url(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["portfolio"] = message.text
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 88:
            return

        elif step == 89:
            return

        elif step == 90:
            posts_table = wwf.load_table(P_POSTS)
            post = posts_table[users_table[user_id]["editing"]["post_id"]]
            if post["type"] == 1:
                ans, error_text = is_suitable_price_fl(message.text)
            elif post["type"] == 2:
                ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["payment_type"] = 2
            posts_table[users_table[user_id]["editing"]["post_id"]]["price"] = float(message.text)
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 91:
            posts_table = wwf.load_table(P_POSTS)
            post = posts_table[users_table[user_id]["editing"]["post_id"]]
            if post["type"] == 1:
                ans, error_text = is_suitable_price_fl(message.text)
            elif post["type"] == 2:
                ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["editing"]["payment_type"] = 3
            users_table[user_id]["editing"]["price"] = float(message.text)
            wwf.save_table(users_table, P_USERS)
            mes.edit_price_2_nm(message)
            return

        elif step == 92:
            posts_table = wwf.load_table(P_POSTS)
            post = posts_table[users_table[user_id]["editing"]["post_id"]]
            if post["type"] == 1:
                ans, error_text = is_suitable_price_2_fl(message.text, users_table[user_id]["editing"]["price"])
            elif post["type"] == 2:
                ans, error_text = is_suitable_price_2_cu(message.text, users_table[user_id]["editing"]["price"])
            if not ans:
                mes.error_message(message, error_text)
                return

            posts_table[users_table[user_id]["editing"]["post_id"]]["payment_type"] = 3
            posts_table[users_table[user_id]["editing"]["post_id"]]["price"] = [0, 0]
            posts_table[users_table[user_id]["editing"]["post_id"]]["price"][0] = users_table[user_id]["editing"]["price"]
            posts_table[users_table[user_id]["editing"]["post_id"]]["price"][1] = float(message.text)
            wwf.save_table(posts_table, P_POSTS)
            mes.send_post_nm(message, users_table[user_id]["editing"]["post_id"])
            return

        elif step == 100:
            return

        elif step == 101:
            ans, error_text = is_suitable_title_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["title"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_description_customer_post_nm(message)
            return

        elif step == 102:
            ans, error_text = is_suitable_description_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["description"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_portfolio_customer_post_nm(message)
            return

        elif step == 103:
            ans, error_text = is_suitable_memo_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["memo"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_portfolio_customer_post_nm(message)
            return

        elif step == 104:
            ans, error_text = is_suitable_contacts_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["contacts"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.set_payment_type_customer_post_nm(message)
            return

        elif step == 105:
            return

        elif step == 106:
            ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["price"] = float(message.text)
            wwf.save_table(users_table, P_USERS)
            mes.is_guarantee_necessary_customer_nm(message)
            return

        elif step == 107:
            ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["price"][0] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.set_range_price_2_customer_nm(message)
            return

        elif step == 108:
            ans, error_text = is_suitable_price_2_cu(message.text, int(users_table[user_id]["customer_post"]["price"][0]))
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["price"][1] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.is_guarantee_necessary_customer_nm(message)
            return

        elif step == 109:
            return

        elif step == 110:
            return

        elif step == 111:
            ans, error_text = is_suitable_title_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["title"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 112:
            ans, error_text = is_suitable_description_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["description"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 113:
            return

        elif step == 114:
            ans, error_text = is_suitable_contacts_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["contacts"] = message.text
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 115:
            return

        elif step == 116:
            return

        elif step == 117:
            ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return
            users_table[user_id]["customer_post"]["payment_type"] = 2
            users_table[user_id]["customer_post"]["price"] = (int(100 * float(message.text)) / 100)
            users_table[user_id]["editing_customer_post"] = {}
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 118:
            ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["editing_customer_post"]["price"][0] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.edit_pbp_nt_2_price_customer_nm(message)
            return

        elif step == 119:
            ans, error_text = is_suitable_price_2_cu(message.text, users_table[user_id]["editing_customer_post"]["price"][0])
            if not ans:
                mes.error_message(message, error_text)
                return
            users_table[user_id]["customer_post"]["payment_type"] = 3
            users_table[user_id]["customer_post"]["price"] = [0, 0]
            users_table[user_id]["customer_post"]["price"][0] = users_table[user_id]["editing_customer_post"]["price"][0]
            users_table[user_id]["customer_post"]["price"][1] = (int(100 * float(message.text)) / 100)
            users_table[user_id]["editing_customer_post"] = {}
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 120:
            ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["price"] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 121:
            ans, error_text = is_suitable_price_cu(message.text)
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["price"][0] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.edit_pbp_price_2_customer_nm(message)
            return

        elif step == 122:
            ans, error_text = is_suitable_price_2_cu(message.text, users_table[user_id]["customer_post"]["price"][0])
            if not ans:
                mes.error_message(message, error_text)
                return

            users_table[user_id]["customer_post"]["price"][1] = (int(100 * float(message.text)) / 100)
            wwf.save_table(users_table, P_USERS)
            mes.preview_post_customer_nm(message, users_table[user_id]["customer_post"], True)
            mes.edit_pbp_menu_customer_nm(message)
            return

        elif step == 123:
            return

        elif step == 124:
            return


@tb.pre_checkout_query_handler(func=lambda query: True)
def check(pre_checkout_query):
    tb.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message="Инопланетяне перехватили платеж")


@tb.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_id = str(message.chat.id)
    if message.successful_payment.invoice_payload == "127":
        order_table = wwf.load_table(P_ORDERS)
        post_id = order_table[user_id]['post_id']
        num = order_table[user_id]['number']
        up_type = order_table[user_id]['type']
        post_table = wwf.load_table(P_POSTS)
        if up_type == 'ap':
            post_table[post_id]['auto_ups'] += num
            post_table[post_id]["auto_ups_type"] = order_table[user_id]['mode']
        else:
            users_table = wwf.load_table(P_USERS)
            users_table[user_id]['manual_ups'] += num
            wwf.save_table(users_table, P_USERS)
        wwf.save_table(post_table, P_POSTS)
        tb.send_message(message.chat.id, "Благодарим за покупку")
    elif message.successful_payment.invoice_payload == "126":
        users_table = wwf.load_table(P_USERS)
        users_table[user_id]["verification_request_was_sent"] = time.time()
        wwf.save_table(users_table, P_USERS)
        mes.confirm_verification_nm(ID_MANAGE_CHANNEL, users_table[user_id])
        mes.paid_verification_nm(message)
        return
    mes.main_menu_nm(message)


def add_user(user_id: int or str):
    user_id = str(user_id)
    # Добавляем в список пользователей
    users_table = wwf.load_table(P_USERS)
    users_table[user_id] = {"user_id": user_id, "condition": 0, "manual_ups": 0, "verified": False, "auto_ups_mode": 0, "buying_post": 0, "editing": {}, "editing_freelance_post": {}, "editing_customer_post": {}, "verification_request_was_sent": -1, "verification_request":{}}
    wwf.save_table(users_table, P_USERS)

    # Добавляем в список, описывающий посты определенного пользователя
    ownerships_table = wwf.load_table(P_OWNERSHIPS)
    ownerships_table[user_id] = []
    wwf.save_table(ownerships_table, P_OWNERSHIPS)

    # Добавляем в список действий пользователя
    actions_table = wwf.load_table(P_ACTIONS)
    actions_table[user_id] = []
    wwf.save_table(actions_table, P_ACTIONS)


def create_temp_freelance_post(user_id: int or str):
    user_id = str(user_id)

    users_table = wwf.load_table(P_USERS)
    users_table[user_id]["freelance_post"] = {"title": None,
                                              "description": None,
                                              "memo": "",
                                              "portfolio": "",
                                              "contacts": "",
                                              "categories": [],
                                              "payment_type": None,
                                              "price": None,
                                              "guarantee": False,
                                              "time_published": None,
                                              "time_upped": None,
                                              "auto_ups": 0,
                                              "auto_ups_type": 0,
                                              "reported": 0,
                                              "users_reported": [],
                                              "report_was_sent": False,

                                              # После публикации нельзя редактировать
                                              "published": False,
                                              "post_id": -1,
                                              "owner_id": user_id,
                                              "type": 1
                                              }
    wwf.save_table(users_table, P_USERS)


def create_temp_customer_post(user_id: int or str):
    user_id = str(user_id)

    users_table = wwf.load_table(P_USERS)
    users_table[user_id]["customer_post"] = {"title": None,
                                             "description": None,
                                             "portfolio": False,
                                             "contacts": "",
                                             "categories": [],
                                             "payment_type": None,
                                             "price": None,
                                             "guarantee": False,
                                             "time_published": None,
                                             "time_upped": None,
                                             "auto_ups": 0,
                                             "auto_ups_type": 0,
                                             "reported": 0,
                                             "users_reported": [],
                                             "report_was_sent": False,

                                             # После публикации нельзя редактировать
                                             "published": False,
                                             "post_id": -1,
                                             "owner_id": user_id,
                                             "type": 2
                                             }
    wwf.save_table(users_table, P_USERS)


def is_suitable_title_fl(text):
    error_text = None
    if len(text) > FREELANCE_TITLE_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить название услуги до " + str(FREELANCE_TITLE_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_description_fl(text):
    error_text = None
    if len(text) > FREELANCE_DESCRIPTION_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить описание услуги до " + str(FREELANCE_DESCRIPTION_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_memo_fl(text):
    error_text = None
    if len(text) > FREELANCE_MEMO_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить памятку до " + str(FREELANCE_MEMO_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_portfolio_fl(text):
    error_text = None
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_contacts_fl(text):
    error_text = None
    if len(text) > FREELANCE_CONTACTS_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить контакты до " + str(FREELANCE_CONTACTS_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_price_fl(text):
    error_text = None
    try:
        text = float(text)
    except ValueError:
        error_text = "Недопустимое значение"
        return False, error_text

    if text < 0 or bool((text // 1000)):
        error_text = "Недопустимое значение"
        return False, error_text

    return True, None


def is_suitable_price_2_fl(text, num1):
    error_text = None
    ans, er_text = is_suitable_price_fl(text)
    if not ans:
        return ans, er_text

    text = float(text)
    if text <= num1:
        error_text = "Второе число не может быть меньше или равно первому"
        return False, error_text

    return True, None


def is_suitable_ups_count(text):
    try:
        text = int(text)
    except ValueError:
        return False, "Неверное значение"

    if text < 1:
        return False, "Минимум 1 штука"
    elif text > 100:
        return False, "Максимум за 1 раз - 100 штук"

    return True, None


def is_suitable_title_cu(text):
    error_text = None
    if len(text) > CUSTOMER_TITLE_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить название услуги до " + str(CUSTOMER_TITLE_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_description_cu(text):
    error_text = None
    if len(text) > CUSTOMER_DESCRIPTION_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить описание услуги до " + str(CUSTOMER_DESCRIPTION_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_memo_cu(text):
    error_text = None
    if len(text) > CUSTOMER_MEMO_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить памятку до " + str(CUSTOMER_MEMO_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_portfolio_cu(text):
    error_text = None
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_contacts_cu(text):
    error_text = None
    if len(text) > CUSTOMER_CONTACTS_LETTERS_LIMIT:
        error_text = "Ошибка! Попробуйте сократить контакты до " + str(CUSTOMER_CONTACTS_LETTERS_LIMIT) + " знаков. (У вас " + str(len(text)) + ")"
        return False, error_text
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_price_cu(text):
    error_text = None
    try:
        text = float(text)
    except ValueError:
        error_text = "Недопустимое значение"
        return False, error_text

    if text < 0 or bool((text // 1000)):
        error_text = "Недопустимое значение"
        return False, error_text

    return True, None


def is_suitable_price_2_cu(text, num1):
    error_text = None
    ans, er_text = is_suitable_price_cu(text)
    if not ans:
        return ans, er_text

    text = float(text)
    if text <= num1:
        error_text = "Второе число не может быть меньше или равно первому"
        return False, error_text

    return True, None


def is_url(text: str):
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    ans = regex.findall(text)
    if len(ans) != 1 or len(text) == 0:
        return False, "Неверный url"
    return True, None


def is_suitable_about_verification(text: str):
    if len(text) > VERIFICATION_ABOUT_LETTERS_LIMIT:
        return False, "Превышен лимит на количество символов, " + str(len(text)) + "/" + str(VERIFICATION_ABOUT_LETTERS_LIMIT)
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_suitable_links_verification(text: str):
    if len(text) > VERIFICATION_LINKS_LETTERS_LIMIT:
        return False, "Превышен лимит на количество символов, " + str(len(text)) + "/" + str(VERIFICATION_LINKS_LETTERS_LIMIT)
    if "<" in text:
        error_text = "Запрещено использовать <"
        return False, error_text
    return True, None


def is_need_to_delete(post):
    if post["reported"] > 15:
        return True
    return False


def a():
    while True:
        post = wwf.load_table(P_POSTS)
        for key, value in post.items():
            if value['auto_ups'] == 0:
                pass
            else:
                if value['auto_ups_type'] == 3 and (time.time() - value['time_upped'] > 21600):
                    post[key]['time_upped'] = time.time()
                    post[key]['auto_ups'] -= 1
                    wwf.save_table(post, P_POSTS)
                    mes.post_nm(ID_POST_CHANNEL, post[key])
                if value['auto_ups_type'] == 2 and (time.time() - value['time_upped'] > 43200):
                    post[key]['time_upped'] = time.time()
                    post[key]['auto_ups'] -= 1
                    wwf.save_table(post, P_POSTS)
                    mes.post_nm(ID_POST_CHANNEL, post[key])
                if value['auto_ups_type'] == 1 and (time.time() - value['time_upped'] > 86400):
                    post[key]['time_upped'] = time.time()
                    post[key]['auto_ups'] -= 1
                    wwf.save_table(post, P_POSTS)
                    mes.post_nm(ID_POST_CHANNEL, post[key])
        dposts_table = wwf.load_table(P_D_POSTS)
        for key, value in dposts_table.items():
            if float(key) > time.time():
                break
            for p in value:
                if p["replace"] == 0:
                    tb.edit_message_reply_markup(chat_id=p["cid"], message_id=p["mid"])
            del dposts_table[key]
        wwf.save_table(dposts_table, P_D_POSTS)
        time.sleep(120)


Thread(target=a).start()


if __name__ == "__main__":
    tb.polling(none_stop=True)
