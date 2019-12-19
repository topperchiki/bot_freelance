#
from constants import *
import messages as mes
import db
from checkers import *
from exceptions import *

#
from telebot import types, apihelper
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
                              time.gmtime(time.time())) + str(
            message.chat.id) + " " + message.text + "\n")
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)

    #  set_user_referral_code(user_id, author_user_id) - Поставить для пользователя user_id реферальный код пользователя author_user_id

    if len(user_step) == 0:
        if len(message.text) > 7:
            ref_code = message.text[8:]
            try:
                u_id, count = db.get_referral_code_info(ref_code)
                count += 1
                db.set_referral_code_user_count(u_id, count)
                if count % 5 == 0 and count != 0:
                    count = db.get_manual_ups(u_id) + 1
                    db.set_manual_ups(u_id, count)

            except Exception:
                tb.send_message(chat_id, 'Неверный код')

        adding_new_user(user_id)
        user_step = 0

    else:
        user_step = user_step[0]

    ban, status = db.get_info_about_user_ban(user_id)

    if ban == True:
        if status == False:
            db.set_notified_ban_status(user_id, True)
            mes.text_message(chat_id,
                             "К сожалению вы заблокированы админиистрацией")

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return
        mes.main_menu_nm(message.chat.id, user_id)
        return


@tb.message_handler(commands=['help'])
def help_and_tips(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(
            message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)

    if len(user_step) == 0:
        adding_new_user(user_id)
        user_step = 0
    else:
        user_step = user_step[0]

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
                              time.gmtime(time.time())) + str(
            message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)

    if len(user_step) == 0:
        adding_new_user(user_id)
        user_step = 0
    else:
        user_step = user_step[0]

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return
        mes.send_posts_page_nm(message.chat.id, user_id, 1)
        return


@tb.callback_query_handler(func=lambda call: True)
def query_handler(call):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(
            call.message.chat.id) + " " + call.data + "\n")

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_step = db.get_user_steps_if_exists(user_id)

    if len(user_step) == 0:
        adding_new_user(user_id)
        user_step = 0
    else:
        user_step = user_step[0]

    # if db.user_id['ban'] == 'banned': #TODO запрос к бд по бану
    #     mes.text_message(chat_id, "К сожалению вы заблокированы админиистрацией")
    #     return

    call_data_lowered = call.data.lower()
    if call_data_lowered == "noanswer":
        return

    elif call.message.chat.type == "private":

        if call_data_lowered == "mainmenu":
            mes.main_menu(chat_id, message_id, user_id)

        elif call_data_lowered == "sidemenu":
            if user_step not in POSSIBLE_COME_TO_SIDEMENU:
                return
            if not bool(db.is_prepare_exist(user_id)):
                db.add_prepare_post(user_id)
            else:
                db.set_prepare_user_categories(user_id, "")

            mes.side_menu(chat_id, message_id, user_id)
            return

        elif call_data_lowered == "paidservices":
            if user_step not in POSSIBLE_COME_TO_PAIDSERVICES:
                return

            mes.paid_service_menu(chat_id, message_id, user_id)
            return

        elif call_data_lowered == "referral":
            mes.generate_referral(user_id, chat_id)
            return

        elif call_data_lowered[:10] == "createpost":
            post_type = (1 if call_data_lowered[11:13] == "fr" else 2)

            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_CREATEFREELANCEPOST:
                    return
                db.set_prepare_user_post_type(user_id, 1)
                mes.categories_post(chat_id, message_id, user_id, post_type=1)
                return

            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_CREATECUSTOMERPOST:
                    return
                db.set_prepare_user_post_type(user_id, 2)
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

                if not db.is_category_exist(parent_category_id):
                    mes.text_message(chat_id, "Неизвестная категория. "
                                              "Возможно она была удалена")
                    return

                category_children = db.get_category_children_if_exists(
                    parent_category_id)

                categories_str = db.get_prepare_user_categories(user_id)[0]
                if categories_str:
                    categories_str += ";" + parent_category_id
                else:
                    categories_str = parent_category_id
                db.set_prepare_user_categories(user_id, categories_str)

                if len(category_children) > 0:
                    mes.subcategories_post(chat_id, message_id,
                                           parent_category_id, user_id,
                                           post_type)
                    return

                parent_category_name = db.get_category_name(parent_category_id)

                ln_pcn = len(parent_category_name)
                if ln_pcn > 10:
                    parent_category_name = "..." + parent_category_name[
                                                   ln_pcn - 7:]

                del ln_pcn

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text=parent_category_name[0] + " ✅",
                    callback_data="noanswer"))

                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

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

                categories_str = db.get_prepare_user_categories(user_id)[
                    0].split(";")

                if len(categories_str) == 1:
                    db.set_prepare_user_categories(user_id, "")
                    mes.categories_post(chat_id, message_id, user_id, post_type)

                elif len(categories_str) == 0:
                    mes.side_menu(chat_id, message_id, user_id)

                else:
                    ind = len(categories_str) - 2
                    category_to_show = categories_str[ind]

                    categories_str = categories_str[:ind + 1]
                    db.set_prepare_user_categories(user_id,
                                                   ';'.join(categories_str))
                    mes.subcategories_post(chat_id, message_id,
                                           category_to_show, user_id, post_type)
                return

        elif call_data_lowered[:12] == "payment_type":
            post_type = (1 if call_data_lowered[13:15] == "fr" else 2)

            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_PAYMENTTYPE_FR:
                    return

            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_PAYMENTTYPE_CU:
                    return

            pay_type = call.data[16:]

            # Проверка на актуальность
            try:
                pay_type = int(pay_type)
            except ValueError:
                mes.text_message(chat_id, "Неверный тип цены")
                return

            if pay_type < 1 or pay_type > 3:
                mes.text_message(chat_id, "Неверный тип цены")
                return

            db.set_prepare_user_payment_type(user_id, pay_type)
            if pay_type == 1:

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    telebot.types.InlineKeyboardButton(text="Договорная ✅",
                                                       callback_data="noanswer"))

                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

                if post_type == 1:
                    mes.is_guarantee_necessary_freelance_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.is_guarantee_necessary_customer_nm(chat_id, user_id)
                return

            elif pay_type == 2:
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    telebot.types.InlineKeyboardButton(text="Фиксированная ✅",
                                                       callback_data="noAnswer"))
                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

                if post_type == 1:
                    mes.set_fixed_price_freelance_nm(chat_id, user_id)
                elif post_type == 2:
                    mes.set_fixed_price_customer_nm(chat_id, user_id)
                return

            elif pay_type == 3:
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    telebot.types.InlineKeyboardButton(text="Диапозон ✅",
                                                       callback_data="noAnswer"))
                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

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

            try:
                ans = call.data[13:]
                ans = bool(ans)
            except ValueError or KeyError:
                mes.text_message(chat_id, "Неверный вариант")
                return

            db.set_prepare_user_guarantee(user_id, ans)
            mes.send_prepared_post_nm(chat_id, user_id)
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
                db.set_prepare_user_portfolio(user_id, "")
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
                    db.set_prepare_user_portfolio(user_id, str(1))
                    keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅",
                                                                    callback_data="noAnswer"))
                else:
                    db.set_prepare_user_portfolio(user_id, "")
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(text="Нет ❌",
                                                           callback_data="noAnswer"))

                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)
                mes.set_contacts_customer_post_nm(chat_id, user_id)
                return

        elif call_data_lowered == "preview_post":
            post_type = (1 if call_data_lowered[13:15] == "fr" else 2)
            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_PREVIEW_POST_FR:
                    return
            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_PREVIEW_POST_CU:
                    return

            mes.send_prepared_post_nm(chat_id, user_id)
            return

        elif call_data_lowered == "post":
            post_type = (1 if call_data_lowered[5:7] == "fr" else 2)
            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_POST_FR:
                    return
            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_POST_CU:
                    return
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

        elif call_data_lowered[:8] == "edit_pbp":
            left_part = call_data_lowered[9:]

            if left_part[:4] == "menu":
                post_type = (1 if left_part[5:7] == "fr" else 2)
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_MENU_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_MENU_CU:
                        return

                db.set_prepare_new_user_categories(user_id, "")
                mes.edit_pbp_menu_nm(chat_id, user_id, post_type)
                return

            elif left_part[:10] == "categories":
                post_type = (1 if left_part[13:15] == "fr" else 2)

                if left_part[11] == "n":
                    if post_type == 1:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_FR:
                            return
                    elif post_type == 2:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_CU:
                            return

                    parent_category_id = call.data[16:]

                    if not db.is_category_exist(parent_category_id):
                        mes.text_message(chat_id, "Неизвестная категория. "
                                                  "Возможно она была удалена")
                        return

                    category_children = db.get_category_children_if_exists(
                        parent_category_id)

                    categories_str = \
                    db.get_prepare_new_user_categories(user_id)[0]
                    if categories_str:
                        categories_str += ";" + parent_category_id
                    else:
                        categories_str = parent_category_id

                    if len(category_children) > 0:
                        db.set_prepare_new_user_categories(user_id,
                                                           categories_str)
                        mes.edit_pbp_categories(chat_id, message_id,
                                                parent_category_id, user_id,
                                                post_type)
                        return

                    db.set_prepare_user_categories(user_id, categories_str)
                    db.set_prepare_new_user_categories(user_id, "")

                    parent_category_name = db.get_category_name(
                        parent_category_id)

                    ln_pcn = len(parent_category_name)
                    if ln_pcn > 10:
                        parent_category_name = "..." + parent_category_name[
                                                       ln_pcn - 7:]

                    del ln_pcn

                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(telebot.types.InlineKeyboardButton(
                        text=parent_category_name[0] + " ✅",
                        callback_data="noanswer"))

                    # Удаляем предыдущую клавиатуру
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)

                    mes.send_prepared_post_nm(chat_id, user_id)

                elif left_part[11] == "b":
                    if post_type == 1:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_BACK_FR:
                            return
                    elif post_type == 2:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_BACK_CU:
                            return

                    categories_str = \
                    db.get_prepare_new_user_categories(user_id)[0].split(";")

                    if len(categories_str) == 1:
                        db.set_prepare_new_user_categories(user_id, "")
                        mes.categories_post(chat_id, message_id, user_id,
                                            post_type)

                    elif len(categories_str) == 0:
                        mes.edit_pbp_menu(chat_id, message_id, user_id)
                        mes.side_menu(chat_id, message_id, user_id)

                    else:
                        ind = len(categories_str) - 2
                        category_to_show = categories_str[ind]

                        categories_str = categories_str[:ind + 1]
                        db.set_prepare_new_user_categories(user_id,
                                                           ';'.join(
                                                               categories_str))
                        mes.edit_pbp_categories(chat_id, message_id,
                                                category_to_show,
                                                user_id, post_type)

                return

            elif left_part == "title":
                post_type = (1 if left_part[6:8] == "fr" else 2)
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_TITLE_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_TITLE_CU:
                        return
                mes.edit_pbp_title_nm(chat_id, user_id, post_type)
                return

            elif left_part == "description":
                post_type = (1 if left_part[12:14] == "fr" else 2)
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_DESCRIPTION_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_DESCRIPTION_CU:
                        return
                mes.edit_pbp_description_nm(chat_id, user_id, post_type)
                return

            elif left_part == "memo":
                if user_step not in POSSIBLE_COME_TO_EDIT_PBP_MEMO:
                    return
                mes.edit_pbp_memo_nm(chat_id, user_id)
                return

            elif left_part == "portfolio":
                post_type = (1 if left_part[10:12] == "fr" else 2)

                if post_type == 1:
                    left_part_another = left_part[13:]
                    if len(left_part_another) > 0 and left_part_another[
                        0] == 'n':
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_NO_PORTFOLIO_FR:
                            return

                        db.set_prepare_user_portfolio(user_id, "")
                        mes.send_prepared_post_nm(chat_id, user_id)
                        return

                    else:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PORTFOLIO_FR:
                            return
                        mes.edit_pbp_portfolio_nm(chat_id, user_id)

                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PORTFOLIO_CU:
                        return

                    mes.edit_pbp_portfolio(chat_id, message_id, user_id)
                    return

            elif left_part == "contacts":
                post_type = (1 if left_part[10:12] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_CONTACTS_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_CONTACTS_CU:
                        return

                mes.edit_pbp_contacts_nm(chat_id, user_id, post_type)
                return

            elif left_part == "payment":
                post_type = (1 if left_part[8:10] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENT_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENT_CU:
                        return

                mes.edit_pbp_payment_menu(chat_id, message_id, user_id)
                return

            elif left_part == "payment_type":
                post_type = (1 if left_part[13:15] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENTTYPE_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENTTYPE_CU:
                        return

                pay_data = call.data[15:]

                if pay_data == "m":  # menu
                    mes.edit_pbp_payment_type(chat_id, message_id, user_id,
                                              post_type)
                    return

                # Проверка на актуальность
                try:
                    pay_type = int(pay_data)
                except ValueError:
                    mes.text_message(chat_id, "Неверный тип цены")
                    return

                if pay_type < 1 or pay_type > 3:
                    mes.text_message(chat_id, "Неверный тип цены")
                    return

                if pay_type == 1:

                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(text="Договорная ✅",
                                                           callback_data="noanswer"))

                    # Удаляем предыдущую клавиатуру
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)

                    mes.send_prepared_post_nm(chat_id, user_id)
                    return

                elif pay_type == 2:
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(
                            text="Фиксированная ✅",
                            callback_data="noAnswer"))
                    # Удаляем предыдущую клавиатуру
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)

                    mes.edit_pbp_fixed_price_nm(chat_id, user_id, post_type)
                    return

                elif pay_type == 3:
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(text="Диапозон ✅",
                                                           callback_data="noAnswer"))
                    # Удаляем предыдущую клавиатуру
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)

                    mes.edit_pbp_range_price_1_nm(chat_id, user_id, post_type)
                    return

            elif left_part == "price":
                post_type = (1 if left_part[6:8] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PRICE_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PRICE_CU:
                        return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    telebot.types.InlineKeyboardButton(text="Изменить цену ✅",
                                                       callback_data=
                                                       "noAnswer"))
                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

                mes.edit_pbp_price_nm(chat_id, user_id, post_type)
                return

            elif left_part == "price_2":
                post_type = (1 if left_part[8:10] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PRICE_2_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PRICE_2_CU:
                        return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    telebot.types.InlineKeyboardButton(text="Изменить диапозон "
                                                            "✅",
                                                       callback_data=
                                                       "noAnswer"))
                # Удаляем предыдущую клавиатуру
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

                mes.edit_pbp_price_range_nm(chat_id, user_id, post_type)
                return

            elif left_part == "guarantee":
                post_type = (1 if left_part[10:12] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_GUARANTEE_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_GUARANTEE_CU:
                        return
                left_part_another = left_part[13:]

                if left_part_another == "y":
                    db.set_prepare_user_guarantee(user_id, True)
                    mes.send_prepared_post_nm(chat_id, user_id)
                    return

                elif left_part_another == "n":
                    db.set_prepare_user_guarantee(user_id, False)
                    mes.send_prepared_post_nm(chat_id, user_id)
                    return

                mes.edit_pbp_guarantee(chat_id, user_id, post_type)
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

    elif call.chat.type == "group" and chat_id in ALLOWED_GROUP_CHATS:
        pass


@tb.message_handler()
def all_left_text_messages(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(
            message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    user_step = db.get_user_steps_if_exists(user_id)
    chat_id = message.chat.id
    message_id = message.message_id

    if len(user_step) == 0:
        adding_new_user(user_id)
        user_step = 0
    else:
        user_step = user_step[0]

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return

        if chat_id in ADMIN_IDS:
            command = message.text.lower()
            handle_admin_command(command, chat_id, message_id, user_id)
            return

        lowered_message = message.text.lower()
        if lowered_message == "назад":
            if user_step == 1:
                return

            elif user_step == 2:
                return

            elif user_step == 3:
                return

            elif user_step == 4:
                return

            elif user_step == 5:
                categories = db.get_prepare_user_categories(user_id)[0]
                categories = categories.split(";")
                index = len(categories) - 2
                db.set_prepare_user_categories(user_id,
                                               ';'.join(categories[:index + 1]))

                if len(categories) == 1:
                    mes.categories_post_nm(chat_id, user_id)
                else:
                    mes.subcategories_post_nm(chat_id, categories[index],
                                              user_id)
                return

            elif user_step == 6:
                mes.set_title_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 7:
                mes.set_description_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 8:
                mes.set_memo_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 9:
                mes.set_portfolio_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 10:
                mes.set_contacts_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 11:
                mes.set_payment_type_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 12:
                mes.set_payment_type_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 13:
                mes.set_range_price_1_freelance_nm(chat_id, user_id)
                return

            elif user_step == 14:
                mes.set_payment_type_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 15:
                mes.is_guarantee_necessary_freelance_nm(chat_id, user_id)
                return

            elif user_step == 16:
                return

            elif user_step == 17:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return

            elif user_step == 18:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return

            elif user_step == 19:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return

            elif user_step == 20:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return

            elif user_step == 21:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return

            elif user_step == 22:
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return

            elif user_step == 23:
                return

            elif user_step == 24:
                mes.edit_pbp_payment_type_nm(chat_id, user_id)
                return

            elif user_step == 25:
                mes.edit_pbp_payment_type_nm(chat_id, user_id)
                return

            elif user_step == 26:
                mes.edit_pbp_fixed_price_nm(chat_id, user_id)
                return

            elif user_step == 27:
                mes.edit_pbp_payment_menu(chat_id, message_id, user_id)
                return

            elif user_step == 28:
                mes.edit_pbp_payment_menu(chat_id, message_id, user_id)
                return

            elif user_step == 29:
                mes.text_message(message, "Необходимо ввести второе число")
                return

            elif user_step == 30:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id)
                return
            #
            # elif user_step == 31:
            #     return
            #
            # elif user_step == 70:
            #     return
            #
            # elif user_step == 71:
            #     return
            #
            # elif user_step == 72:
            #     mes.buying_ups_menu_nm(message,
            #                            users_table[user_id]["buying_post"])
            #     return
            #
            # elif user_step == 73:
            #     mes.buying_ups_menu_nm(message,
            #                            users_table[user_id]["buying_post"])
            #     return
            #
            # elif user_step == 74:
            #     return
            #
            # elif user_step == 75:
            #     mes.paid_service_menu_nm(message)
            #     return
            #
            # elif user_step == 76:
            #     mes.write_about_yourself_ver_nm(message)
            #     return
            #
            # elif user_step == 77:
            #     mes.send_links_ver_nm(message)
            #     return
            #
            # elif user_step == 78:
            #     return
            #
            # elif user_step == 80:
            #     return
            #
            # elif user_step == 81:
            #     return
            #
            # elif user_step == 82:
            #
            #     mes.edit_post_menu_nm(message, users_table[user_id]["editing"][
            #         "post_id"])
            #     return
            #
            # elif user_step == 83:
            #     mes.edit_post_menu_nm(message, users_table[user_id]["editing"][
            #         "post_id"])
            #     return
            #
            # elif user_step == 84:
            #     mes.edit_post_menu_nm(message, users_table[user_id]["editing"][
            #         "post_id"])
            #     return
            #
            # elif user_step == 85:
            #     mes.edit_post_menu_nm(message, users_table[user_id]["editing"][
            #         "post_id"])
            #     return
            #
            # elif user_step == 86:
            #     mes.edit_post_menu_nm(message, users_table[user_id]["editing"][
            #         "post_id"])
            #     return
            #
            # elif user_step == 87:
            #     return
            #
            # elif user_step == 88:
            #     return
            #
            # elif user_step == 89:
            #     return
            #
            # elif user_step == 90:
            #     wwf.save_table(users_table, P_USERS)
            #     mes.edit_pay_nm(message,
            #                     users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 91:
            #     wwf.save_table(users_table, P_USERS)
            #     mes.edit_pay_nm(message,
            #                     users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 92:
            #     wwf.save_table(users_table, P_USERS)
            #     mes.edit_price_1_nm(message)
            #     return

            elif user_step == 100:
                return

            elif user_step == 101:
                categories = db.get_prepare_user_categories(user_id)[0]
                categories = categories.split(";")
                index = len(categories) - 2
                db.set_prepare_user_categories(user_id,
                                               ';'.join(categories[:index + 1]))

                if len(categories) == 1:
                    mes.categories_post_nm(chat_id, user_id, post_type=2)
                else:
                    mes.subcategories_post_nm(chat_id, categories[index],
                                              user_id, post_type=2)
                return

            elif user_step == 102:
                mes.set_title_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 103:
                mes.set_description_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 104:
                mes.set_portfolio_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 105:
                mes.set_contacts_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 106:
                mes.set_payment_type_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 107:
                mes.set_payment_type_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 108:
                mes.set_range_price_1_customer_nm(chat_id, user_id)

            elif user_step == 109:
                mes.set_payment_type_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 110:
                mes.is_guarantee_necessary_customer_nm(chat_id, user_id)
                return

            elif user_step == 111:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

            elif user_step == 112:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

            elif user_step == 113:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

            elif user_step == 114:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

            elif user_step == 115:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

            elif user_step == 116:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

            elif user_step == 117:
                mes.edit_pbp_payment_type_nm(chat_id, user_id, 2)
                return

            elif user_step == 118:
                mes.edit_pbp_payment_type_nm(chat_id, user_id, 2)
                return

            elif user_step == 119:
                mes.edit_pbp_range_price_1_nm(chat_id, user_id, 2)
                return

            elif user_step == 120:
                mes.edit_pbp_payment_type_nm(chat_id, user_id, 2)
                return

            elif user_step == 121:
                mes.edit_pbp_payment_type_nm(chat_id, user_id, 2)
                return

            elif user_step == 122:
                mes.text_message(message, "Необходимо ввести второе число")
                return

            elif user_step == 123:
                mes.send_prepared_post_nm(chat_id, user_id, True)
                mes.edit_pbp_menu_nm(chat_id, user_id, 2)
                return

        elif lowered_message == "в главное меню" or lowered_message == \
                "главное меню":

            mes.main_menu_nm(chat_id, user_id)

        else:
            if user_step == 1:
                return

            elif user_step == 2:
                return

            elif user_step == 3:
                return

            elif user_step == 4:
                return

            elif user_step == 5:
                ans, error_text = is_suitable_title_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_title(user_id, message.text)
                mes.set_description_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 6:
                ans, error_text = is_suitable_description_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_description(user_id, message.text)
                mes.set_memo_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 7:
                ans, error_text = is_suitable_memo_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_memo(user_id, message.text)
                mes.set_portfolio_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 8:
                ans, error_text = is_url(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_portfolio(user_id, message.text)
                mes.set_contacts_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 9:
                ans, error_text = is_suitable_contacts_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_contacts(user_id, message.text)
                mes.set_payment_type_freelance_post_nm(chat_id, user_id)
                return

            elif user_step == 10:
                return

            elif user_step == 11:
                ans, error_text = is_suitable_price_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id, message.text)
                mes.is_guarantee_necessary_freelance_nm(chat_id, user_id)
                return

            elif user_step == 12:
                ans, error_text = is_suitable_price_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id, message.text)
                mes.set_range_price_2_freelance_nm(chat_id, user_id)
                return

            elif user_step == 13:
                min_price = db.get_prepare_user_price(user_id)[0]
                ans, error_text = is_suitable_price_2_fl(message.text,
                                                         float(min_price))
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id,
                                          min_price + ";" + message.text)
                mes.is_guarantee_necessary_freelance_nm(chat_id, user_id)
                return

            elif user_step == 14:
                return

            elif user_step == 15:
                return

            elif user_step == 16:
                return

            elif user_step in (17, 111):
                if user_step == 17:
                    ans, error_text = is_suitable_title_fl(message.text)
                else:
                    ans, error_text = is_suitable_title_cu(message.text)

                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_title(user_id, message.text)
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step in (18, 112):
                if user_step == 18:
                    ans, error_text = is_suitable_description_fl(message.text)
                else:
                    ans, error_text = is_suitable_description_cu(message.text)

                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_description(user_id, message.text)
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step == 19:
                ans, error_text = is_suitable_memo_fl(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_memo(user_id, message.text)
                mes.set_memo_freelance_post_nm(chat_id, user_id)
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step == 20:
                ans, error_text = is_url(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_portfolio(user_id, message.text)
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step in (21, 114):
                if user_step == 21:
                    ans, error_text = is_suitable_contacts_fl(message.text)
                else:
                    ans, error_text = is_suitable_contacts_cu(message.text)

                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_contacts(user_id, message.text)
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step == 22:
                return

            elif user_step == 23:
                return

            elif user_step in (24, 117):
                if user_step == 24:
                    ans, error_text = is_suitable_price_fl(message.text)
                else:
                    ans, error_text = is_suitable_price_cu(message.text)

                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_payment_info(user_id, 2, message.text)

                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step in (25, 118):
                if user_step == 25:
                    ans, error_text = is_suitable_price_fl(message.text)
                else:
                    ans, error_text = is_suitable_price_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_new_user_price(user_id,
                                              int(100 * float(
                                                  message.text)) / 100)
                if user_step == 25:
                    mes.edit_pbp_range_price_1_nm(chat_id, user_id, 1)
                else:
                    mes.edit_pbp_range_price_1_nm(chat_id, user_id, 2)
                return

            elif user_step in (26, 119):

                price1 = db.get_prepare_new_user_price(user_id)
                if user_step == 26:
                    ans, error_text = is_suitable_price_2_fl(message.text, float(price1))
                else:
                    ans, error_text = is_suitable_price_2_cu(message.text,
                                                             float(price1))
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_payment_info(user_id, 3,
                                            price1 + ";" + str(int(100 * float(
                                                  message.text)) / 100))
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step in (27, 120):
                if user_step == 27:
                    ans, error_text = is_suitable_price_fl(message.text)
                else:
                    ans, error_text = is_suitable_price_cu(message.text)

                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id, str(int(100 * float(
                                                  message.text)) / 100))
                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step in (28, 121):
                if user_step == 28:
                    ans, error_text = is_suitable_price_fl(message.text)
                else:
                    ans, error_text = is_suitable_price_cu(message.text)

                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                a = db.get_prepare_user_price(user_id)
                db.set_prepare_user_price(user_id,
                                          str(int(100 * float(
                                              message.text)) / 100) + ";"
                                          + a.split(";")[1])

                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step in (29, 122):

                a = db.get_prepare_user_price(user_id).split(";")
                if user_step == 29:
                    ans, error_text = is_suitable_price_2_fl(message.text, float(a[0]))
                else:
                    ans, error_text = is_suitable_price_2_cu(message.text,
                                                             float(a[0]))
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id, a[0] + ";" +
                                          str(int(100 * float(
                                              message.text)) / 100))

                mes.send_prepared_post_nm(chat_id, user_id)
                return

            elif user_step == 30:
                return

            elif user_step == 31:
                mes.back_prepare_post_menu(chat_id, message_id, user_id)
                return

            elif user_step == 70:
                return

            elif user_step == 71:
                return
            #
            # elif user_step == 72:
            #     ans, error_text = is_suitable_ups_count(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #     mes.bill(chat_id, user_id)
            #     return
            #
            # elif user_step == 73:
            #     ans, error_text = is_suitable_ups_count(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #     mes.bill(chat_id, user_id)
            #     return
            #
            # elif user_step == 74:
            #     return
            #
            # elif user_step == 75:
            #     if users_table[user_id]["verification_request_was_sent"] != -1:
            #         return
            #     ans, error_text = is_suitable_about_verification(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #     users_table[user_id]["verification_request"][
            #         "about"] = message.text
            #     wwf.save_table(users_table, P_USERS)
            #     mes.send_links_ver_nm(chat_id, user_id)
            #     return
            #
            # elif user_step == 76:
            #     if users_table[user_id]["verification_request_was_sent"] != -1:
            #         return
            #     ans, error_text = is_suitable_links_verification(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #     users_table[user_id]["verification_request"][
            #         "links"] = message.text
            #     wwf.save_table(users_table, P_USERS)
            #     mes.preview_verification_request_nm(message,
            #                                         users_table[user_id])
            #     return
            #
            # elif user_step == 77:
            #     return
            #
            # elif user_step == 78:
            #     return
            #
            # elif user_step == 80:
            #     return
            #
            # elif user_step == 81:
            #     return
            #
            # elif user_step == 82:
            #     posts_table = wwf.load_table(P_POSTS)
            #     post = posts_table[users_table[user_id]["editing"]["post_id"]]
            #     if post["type"] == 1:
            #         ans, error_text = is_suitable_title_fl(message.text)
            #     elif post["type"] == 2:
            #         ans, error_text = is_suitable_title_cu(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "title"] = message.text
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 83:
            #     posts_table = wwf.load_table(P_POSTS)
            #     post = posts_table[users_table[user_id]["editing"]["post_id"]]
            #     if post["type"] == 1:
            #         ans, error_text = is_suitable_description_fl(message.text)
            #     elif post["type"] == 2:
            #         ans, error_text = is_suitable_description_cu(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "description"] = message.text
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 84:
            #     posts_table = wwf.load_table(P_POSTS)
            #     ans, error_text = is_suitable_memo_fl(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "memo"] = message.text
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 85:
            #     posts_table = wwf.load_table(P_POSTS)
            #     post = posts_table[users_table[user_id]["editing"]["post_id"]]
            #     if post["type"] == 1:
            #         ans, error_text = is_suitable_contacts_fl(message.text)
            #     elif post["type"] == 2:
            #         ans, error_text = is_suitable_contacts_cu(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "contacts"] = message.text
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 86:
            #     posts_table = wwf.load_table(P_POSTS)
            #     ans, error_text = is_url(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "portfolio"] = message.text
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 87:
            #
            #     posts_table = wwf.load_table(P_POSTS)
            #     ans, error_text = is_url(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "portfolio"] = message.text
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 88:
            #     return
            #
            # elif user_step == 89:
            #     return
            #
            # elif user_step == 90:
            #     posts_table = wwf.load_table(P_POSTS)
            #     post = posts_table[users_table[user_id]["editing"]["post_id"]]
            #     if post["type"] == 1:
            #         ans, error_text = is_suitable_price_fl(message.text)
            #     elif post["type"] == 2:
            #         ans, error_text = is_suitable_price_cu(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "payment_type"] = 2
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "price"] = float(message.text)
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return
            #
            # elif user_step == 91:
            #     posts_table = wwf.load_table(P_POSTS)
            #     post = posts_table[users_table[user_id]["editing"]["post_id"]]
            #     if post["type"] == 1:
            #         ans, error_text = is_suitable_price_fl(message.text)
            #     elif post["type"] == 2:
            #         ans, error_text = is_suitable_price_cu(message.text)
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     users_table[user_id]["editing"]["payment_type"] = 3
            #     users_table[user_id]["editing"]["price"] = float(message.text)
            #     wwf.save_table(users_table, P_USERS)
            #     mes.edit_price_2_nm(chat_id, user_id)
            #     return
            #
            # elif user_step == 92:
            #     posts_table = wwf.load_table(P_POSTS)
            #     post = posts_table[users_table[user_id]["editing"]["post_id"]]
            #     if post["type"] == 1:
            #         ans, error_text = is_suitable_price_2_fl(message.text,
            #                                                  users_table[
            #                                                      user_id][
            #                                                      "editing"][
            #                                                      "price"])
            #     elif post["type"] == 2:
            #         ans, error_text = is_suitable_price_2_cu(message.text,
            #                                                  users_table[
            #                                                      user_id][
            #                                                      "editing"][
            #                                                      "price"])
            #     if not ans:
            #         mes.text_message(chat_id, error_text)
            #         return
            #
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "payment_type"] = 3
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "price"] = [0, 0]
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "price"][0] = users_table[user_id]["editing"]["price"]
            #     posts_table[users_table[user_id]["editing"]["post_id"]][
            #         "price"][1] = float(message.text)
            #     wwf.save_table(posts_table, P_POSTS)
            #     mes.send_post_nm(message,
            #                      users_table[user_id]["editing"]["post_id"])
            #     return

            elif user_step == 100:
                return

            elif user_step == 101:
                ans, error_text = is_suitable_title_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_title(user_id, message.text)
                mes.set_description_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 102:
                ans, error_text = is_suitable_description_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_description(user_id, message.text)
                mes.set_portfolio_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 103:
                ans, error_text = is_suitable_memo_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_memo(user_id, message.text)
                mes.set_portfolio_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 104:
                ans, error_text = is_suitable_contacts_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_contacts(user_id, message.text)
                mes.set_payment_type_customer_post_nm(chat_id, user_id)
                return

            elif user_step == 105:
                return

            elif user_step == 106:
                ans, error_text = is_suitable_price_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id, message.text)
                mes.is_guarantee_necessary_customer_nm(chat_id, user_id)
                return

            elif user_step == 107:
                ans, error_text = is_suitable_price_cu(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id, message.text)
                mes.set_range_price_2_customer_nm(chat_id, user_id)
                return

            elif user_step == 108:
                min_price = db.get_prepare_user_price(user_id)[0]
                ans, error_text = is_suitable_price_2_cu(message.text,
                                                         float(min_price))
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_prepare_user_price(user_id,
                                          min_price + ";" + message.text)
                mes.is_guarantee_necessary_customer_nm(chat_id, user_id)
                return

            elif user_step == 109:
                return

            elif user_step == 110:
                return

            elif user_step == 113:
                return

            elif user_step == 115:
                return

            elif user_step == 116:
                return
            elif user_step == 123:
                return

            elif user_step == 124:
                return

    elif message.chat.type == "public":

        if chat_id in ADMIN_IDS:
            command = message.text.lower()
            handle_admin_command(command, chat_id, message_id, user_id)


#
def handle_admin_command(command: str, chat_id: str or int,
                         message_id: str or int, user_id: str or int):
    if str(command[:9]) == '/unverify':
        try:
            user_id_to_unverify = command[10:]
            if user_id_to_unverify[-1] == "]":
                user_id_to_unverify = user_id_to_unverify[:-1]

            user_id_to_unverify = int(user_id_to_unverify)

        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return

        db.set_user_verification_status(user_id_to_unverify, False)
        mes.text_message(chat_id,
                         "Если пользователь с таким ID существует, то его данные обновлены")
        return

    elif command[:7] == "/verify":
        try:
            user_id_to_verify = command[8:]
            if user_id_to_verify[-1] == "]":
                user_id_to_verify = user_id_to_verify[:-1]
            user_id_to_verify = int(user_id_to_verify)
        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return

        db.set_user_verification_status(user_id_to_verify, True)
        mes.text_message(chat_id,
                         "Если пользователь с таким ID существует, то его данные обновлены")
        return

    elif command[:10] == "/user_info":
        pass

    elif command[:9] == "/ban_user":
        try:
            user_id_to_ban = command[10:]
            if user_id_to_ban[-1] == "]":
                user_id_to_ban = user_id_to_ban[:-1]

            user_id_to_ban = int(user_id_to_ban)
        except ValueError:
            mes.text_message(chat_id, "Неверный формат id")
            return

        db.give_user_ban(
            user_id_to_ban)  # Todo присвоить данному айди статус "banned" для оптимизации можно удалить всю остальную информацию, можно не трогать
        mes.text_message(chat_id,
                         "Пользователь успешно забанен, его объявления удалены, автоподьемы обнулены, доступ к платформе заблокирован ")
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
            user_id_to_ref, code)  # Todo пихнуть код в бд
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
def adding_new_user(user_id: str):
    db.add_user(user_id, int(time.time()))


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
                    db.set_next_post_up_in_auto_post(action[1], action[2] - 1,
                                                     tt + action[3])
                else:
                    db.delete_auto_action_with_post_id(action[1])

            elif actions[0] == 2:
                tb.edit_message_reply_markup(chat_id=ID_POST_CHANNEL,
                                             message_id=action[5])
                db.delete_auto_action_with_message_id(action[5])
        time.sleep(120)


#
if __name__ == "__main__":
    Thread(target=auto_actions).start()

    tb.polling(none_stop=True)
