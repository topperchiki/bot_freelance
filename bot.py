#
import work_with_files as wwf
from constants import *
import messages as mes
import db
from exceptions import *

#
from telebot import types
import telebot
import random
import time
import re
from threading import Thread


tb = telebot.TeleBot(TOKEN)


@tb.message_handler(commands=['start'])
def start_menu(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(message.chat.id) + " " + message.text + "\n")
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)

    # if message.text>7 :
    #     ref_code = message.text[8:]
    #     db.add_point_to_ref(user_id)#TODO +1 человек к приглашенным
    #     if db.poin_to_ref(user_id):
    #         #даём один ручной ап
    #         pass
    #
    # if db.user_id['ban'] == 'banned': #TODO запрос к бд по бану
    #     mes.text_message(chat_id, "К сожалению вы заблокированы админиистрацией")
    #     return

    if isinstance(user_step, bool) and not user_step:
        db.add_user(user_id, int(time.time()))
        user_step = 0

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return
        mes.main_menu_nm(chat_id, user_id)
        return


@tb.callback_query_handler(func=lambda call: True)
def query_handler(call):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(call.message.chat.id) + " " + call.data + "\n")

    user_id = call.from_user.id
    chat_id = call.chat.id
    message_id = call.message.message_id
    user_step = db.get_user_steps_if_exists(user_id)

    if isinstance(user_step, bool) and not user_step:
        db.add_user(user_id, int(time.time()))
        user_step = 0

    # if db.user_id['ban'] == 'banned': #TODO запрос к бд по бану
    #     mes.text_message(chat_id, "К сожалению вы заблокированы админиистрацией")
    #     return

    call_data_lowered = call.data.lower()
    if call_data_lowered == "noanswer":
        return

    elif call.chat.type == "private":

        if call_data_lowered == "mainmenu":
            mes.main_menu_nm(chat_id, user_id)

        elif call_data_lowered == "sidemenu":
            if user_step not in POSSIBLE_COME_TO_SIDEMENU:
                return

            mes.side_menu(chat_id, message_id, user_id)
            return

        elif call_data_lowered == "paidservices":
            if user_step not in POSSIBLE_COME_TO_PAIDSERVICES:
                return

            mes.paid_service_menu(chat_id, message_id, user_id)
            return
        elif call_data_lowered == "referal":
            mes.generate_referal(user_id,chat_id)
            return

        elif call_data_lowered == "createpost":
            post_type = (1 if call_data_lowered[10:12] == "fr" else 2)

            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_CREATEFREELANCEPOST:
                    return
                mes.categories_post(chat_id, message_id, user_id, post_type=1)
                return

            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_CREATECUSTOMERPOST:
                    return
                mes.categories_post(chat_id, message_id, user_id, post_type=2)

            return

        elif call_data_lowered[:8] == "category":
            post_type = (1 if call_data_lowered[9:11] == "fr" else 2)

            if call_data_lowered[12] == "n":
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_CATEGORY_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_CATEGORY_CU:
                        return

                parent_category_id = call.data[14:]

                category_children = db.get_category_children_if_exists(parent_category_id)
                if not category_children:
                    mes.text_message(chat_id, "Неизвестная категория. Возможно она была удалена")
                    return

                category_children = category_children.split(";")

                categories_str = db.get_user_categories(user_id)
                categories_str += ";" + parent_category_id
                db.set_user_categories(user_id, categories_str)

                if len(category_children) > 0:
                    mes.subcategories_post(chat_id, message_id, parent_category_id)
                    return

                parent_category_name = db.get_category_name(parent_category_id)

                ln_pcn = len(parent_category_name)
                if ln_pcn > 10:
                    parent_category_name = "..." + parent_category_name[ln_pcn - 7:]

                del ln_pcn

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(text=parent_category_name + " ✅", callback_data="noanswer"))

                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)

                if post_type == 1:
                    mes.set_title_freelance_post_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.set_title_customer_post_nm(chat_id, user_id)
                return

            elif call_data_lowered[12] == "b":
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_CATEGORY_BACK_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_CATEGORY_BACK_CU:
                        return

                categories_str = db.get_user_categories(user_id).split(";")

                if len(categories_str) == 1:
                    db.set_user_categories(user_id, "")
                    mes.categories_post(chat_id, message_id, user_id)

                elif len(categories_str) == 0:
                    mes.side_menu(message_id, user_id)

                else:
                    ind = len(categories_str) - 1
                    category_to_show = ""
                    while categories_str[ind] != ";":
                        category_to_show += categories_str[ind]
                        ind -= 1

                    categories_str = categories_str[:ind]
                    db.set_user_categories(user_id, categories_str)
                    mes.subcategories_post(message_id, category_to_show)
                return

        elif call_data_lowered[:12] == "payment_type":
            post_type = (1 if call_data_lowered[13:15] == "fr" else 2)

            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_PAYMENTTYPE_FR:
                    return

            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_PAYMENTTYPE_CU:
                    return

            pay_type = call.data[15:]

            # Проверка на актуальность
            try:
                pay_type = int(pay_type)
            except ValueError:
                mes.text_message(chat_id, "Неверный тип цены")
                return

            if pay_type < 1 or pay_type > 3:
                mes.text_message(chat_id, "Неверный тип цены")
                return

            db.set_user_payment_type(user_id, pay_type)
            if pay_type == 1:

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(text="Договорная ✅", callback_data="noanswer"))

                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)

                if post_type == 1:
                    mes.is_guarantee_necessary_freelance_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.is_guarantee_necessary_customer_nm(chat_id, user_id)
                return

            elif pay_type == 2:
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(text="Фиксированная ✅", callback_data="noAnswer"))
                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)

                if post_type == 1:
                    mes.set_fixed_price_freelance_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.set_fixed_price_customer_nm(chat_id, user_id)
                return

            elif pay_type == 3:
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(text="Диапозон ✅", callback_data="noAnswer"))
                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)

                if post_type == 1:
                    mes.set_range_price_1_freelance_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.set_range_price_1_customer_nm(chat_id, user_id)
                return
            return

        elif call_data_lowered[:9] == "guarantee":
            post_type = (1 if call_data_lowered[10:12] == "fr" else 2)

            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_GUARANTEE_FR:
                    return
            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_GUARANTEE_CU:
                    return

            ans = call.data[13]
            try:
                ans = bool(ans)
            except ValueError:
                mes.text_message(chat_id, "Неверный вариант")
                return

            db.set_user_guarantee(user_id, ans)
            mes.preview_post_nm(chat_id, user_id)
            return

        elif call_data_lowered[:9] == "portfolio":
            post_type = (1 if call_data_lowered[10:12] == "fr" else 2)

            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_SKIP_PORTFOLIO:
                    return
            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_PORTFOLIO_CU:
                    return
            answer = call_data_lowered[13:]
            if answer == "skip":
                db.set_user_portfolio(user_id, "")
                if post_type == 1:
                    mes.set_contacts_freelance_post_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.set_contacts_customer_post_nm(chat_id, user_id)
                return

            else:
                if post_type != 2:
                    return

                try:
                    answer = bool(answer)
                except ValueError:
                    return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                if answer:
                    db.set_user_portfolio(user_id, str(1))
                    keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))
                else:
                    db.set_user_portfolio(user_id, "")
                    keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ❌", callback_data="noAnswer"))

                tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
                mes.set_contacts_customer_post_nm(chat_id, user_id)
                return

        elif call_data_lowered == "preview_post":
            if user_step not in POSSIBLE_COME_TO_PREVIEW_POST:
                return
            mes.preview_post_nm(chat_id, user_id)

        elif call_data_lowered == "post":
            if user_step not in POSSIBLE_COME_TO_POST:
                return

            new_id = random.randint(100000, 999999)
            while db.is_post_id_used(new_id):
                new_id = random.randint(100000, 999999)

            new_id = str(new_id)
            # # TODO FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            # ans = mes.post_nm(ID_POST_CHANNEL, users_table[user_id]["freelance_post"])
            # posts_table[new_id] = users_table[user_id]["freelance_post"]
            # posts_table[new_id]["time_published"] = time.time()
            # posts_table[new_id]["time_upped"] = posts_table[new_id]["time_published"]
            # ownership_table[user_id].append(new_id)
            # wwf.save_table(ownership_table, P_OWNERSHIPS)
            #
            # posts_table[new_id]["published"] = True
            #
            # wwf.save_table(posts_table, P_POSTS)
            # dposts_table = wwf.load_table(P_D_POSTS)
            # t = posts_table[new_id]["time_published"] + 169200
            # if t in dposts_table:
            #     dposts_table[t].append({"cid": ID_POST_CHANNEL, "mid": ans.message_id, "replace": 0})
            # else:
            #     dposts_table[t] = [{"cid": ID_POST_CHANNEL, "mid": ans.message_id, "replace": 0}]
            # wwf.save_table(dposts_table, P_D_POSTS)
            #
            # keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            # keyboard.add(telebot.types.InlineKeyboardButton(text="Опубликовано ✅", callback_data="noAnswer"))
            # tb.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
            #                              reply_markup=keyboard)
            # mes.posted(call.message, new_id)
            # return

        elif call_data_lowered[:8] == "postpage":
            page = call_data_lowered[9:]
            try:
                page = int(page)
            except ValueError:
                mes.text_message(chat_id, "Нет такой страницы")
                return

            mes.send_posts_page(chat_id, message_id, user_id, page)
            return

        # elif call_data_lowered == "verification":
        #
        # elif call_data_lowered == "payverification":
        #
        # elif call_data_lowered[:14] == "buyingupsmenu":
        #
        # elif call_data_lowered[:14] == "buyingautoups":
        #
        # elif call_data_lowered[:18] == "buyingautoupsmode":
        #
        # elif call_data_lowered[:16] == "buyingmanualups":
        #
        # elif call_data_lowered[:8] == "getpost":
        #
        # elif call_data_lowered[:2] == "up":
        #
        # elif call_data_lowered[:4] == "edit":
        #     left_part = call_data_lowered[4:]
        #     if left_part == "title":
        #
        #     elif left_part == "guarantee_yes":
        #
        #     elif left_part == "guarantee_no":
        #
        #     elif left_part == "portfolio_yes":
        #
        #     elif left_part == "portfolio_no":
        #
        #     elif left_part == "description":
        #
        #     elif left_part == "memo":
        #
        #     elif left_part == "portfolio":
        #
        #     elif left_part == "guarantee":
        #
        #     elif left_part == "contacts":
        #
        #     elif left_part == "categories":
        #
        #     elif left_part == "categories_1":
        #
        #     elif left_part == "categories_b":
        #
        #     elif left_part == "portfolio_delete":
        #
        #     elif left_part == "pay_type1":
        #
        #     elif left_part == "pay_type2":
        #
        #     elif left_part == "pay_type3":
        #
        #     elif left_part == "payment":
        #
        # elif call_data_lowered[:8] == "edit_pbp":
        #     left_part = call_data_lowered[9:]
        #     if left_part == "menu":
        #     elif left_part[:10] == "categories":
        #         if left_part[11] == "n":
        #         elif left_part[11] == "b":
        #     elif left_part == "title":
        #     elif left_part == "description":
        #     elif left_part == "memo":
        #     elif left_part == "portfolio":
        #     elif left_part == "no_portfolio":
        #     elif left_part == "contacts":
        #     elif left_part == "payment":
        #     elif left_part == "payment_type":
        #     elif left_part == "payment_type_2_fr:":
        #     elif left_part == "price":
        #     elif left_part == "price_2":
        #     elif left_part == "guarantee":
        #     elif left_part == "guarantee_yes":
        #     elif left_part == "guarantee_no":

    elif call.chat.type == "group" and chat_id in ALLOWED_GROUP_CHATS:
        pass


@tb.message_handler(commands=['help'])
def help_and_tips(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)

    if isinstance(user_step, bool) and not user_step:
        db.add_user(user_id, int(time.time()))
        user_step = 0

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return
        mes.help_nm(message.chat.id)
        return


@tb.message_handler(commands=['myposts'])
def help_and_tips(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)

    if isinstance(user_step, bool) and not user_step:
        db.add_user(user_id, int(time.time()))
        user_step = 0

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return
        mes.send_posts_page_nm(message.chat.id, user_id, 1)
        return


@tb.message_handler()
def all_left_commands(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)
    chat_id = message.chat.id
    message_id = message.message_id

    if isinstance(user_step, bool) and not user_step:
        db.add_user(user_id, int(time.time()))
        user_step = 0

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return

        if chat_id in ADMIN_IDS:
            command = message.text.lower()
            handle_admin_command(command, chat_id, message_id, user_id)

    elif message.chat.type == "public":

        if chat_id in ALLOWED_GROUP_CHATS:
            command = message.text.lower()
            handle_admin_command(command, chat_id, message_id, user_id)


#
def handle_admin_command(command: str, chat_id: str or int, message_id: str or int, user_id: str or int):

    if command[:9] == "/unverify":
        user_id_to_unverify = command[10:]
        if user_id_to_unverify[-1] == "]":
            user_id_to_unverify = user_id_to_unverify[:-1]

        try:
            user_id_to_unverify = int(user_id_to_unverify)

        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return

        db.set_user_verification_status(user_id_to_unverify, False)

        mes.text_message(chat_id, "Если пользователь с таким ID существует, то его данные обновлены")
        return

    elif command[:7] == "/verify":
        user_id_to_verify = command[8:]
        if user_id_to_verify[-1] == "]":
            user_id_to_verify = user_id_to_verify[:-1]

        try:
            user_id_to_verify = int(user_id_to_verify)
        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return

        db.set_user_verification_status(user_id_to_verify, True)
        mes.text_message(chat_id, "Если пользователь с таким ID существует, то его данные обновлены")
        return

    elif command[:10] == "/user_info":
        pass

    elif command[:9] == "/ban_user":
        user_id_to_ban = command[10:]
        if user_id_to_ban[-1] == "]":
            user_id_to_ban = user_id_to_ban[:-1]
        try:
            user_id_to_ban = int(user_id_to_ban)
        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return

        db.give_user_ban(user_id_to_ban)  #Todo присвоить данному айди статус "banned" для оптимизации можно удалить всю остальную информацию, можно не трогать
        mes.text_message(chat_id, "Пользователь успешно забанен, его объявления удалены, автоподьемы обнулены, доступ к платформе заблокирован ")
        return
    elif command[:12] == "/delete_user":
        pass

    elif command[:11] == "/user_posts":
        pass

    elif command[:10] == "/hide_rate":
        pass

    elif command[:12] == "/delete_rate":
        pass

    elif command[:12] == "/create_rate":
        pass

    elif command[:10] == "/show_rate":
        pass

    elif command[:18] == "/set_referral_code":
        # До 30 символов! (включительно)
        user_id_to_ref = command[19:]
        if user_id_to_ref[-1] == "]":
            user_id_to_ban = user_id_to_ref[:-1]
        try:
            user_id_to_ref = int(user_id_to_ref)
        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return
        mes.text_message(chat_id,
                         "Отправьте пожалуйста код для реферальной ссылки")
        code = mes.take_text_mes()
        db.give_user_ref(
            user_id_to_ref,code)  # Todo пихнуть код в бд
        mes.text_message(chat_id,
                         "Пользователю успешно присвоен реферальный код ")
        return

    elif command[:11] == "/list_posts":
        pass

    elif command[:12] == "/delete_post":
        pass

    elif command[:12] == "/post_info":
        pass

    elif command[:12] == "/clear_cache":
        pass


#
def auto_actions():
    while True:
        actions = db.get_available_auto_actions(time.time())
        # [0] action_type
        #   1 [1] post_id, counts, plus_time, rate_id, [5] message_id

        for action in actions:
            if action[0] == 1:
                mes.send_post(ID_POST_CHANNEL, action[1])
                tt = time.time()
                db.set_post_last_up_and_counts(action[1], tt, action[2] - 1)
                if action[2] > 1:
                    db.set_next_post_up_in_auto_post(action[1], action[2] - 1, tt + action[3])
                else:
                    db.delete_auto_action_with_post_id(action[1])

            elif actions[0] == 2:
                tb.edit_message_reply_markup(chat_id=ID_POST_CHANNEL, message_id=action[5])
                db.delete_auto_action_with_message_id(action[5])
        time.sleep(120)


#
if __name__ == "__main__":
    Thread(target=auto_actions).start()

    tb.polling(none_stop=True)