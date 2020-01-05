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
    user_info = db.get_user_step_ban_status_is_admin(user_id)

    if len(user_info) == 0:
        adding_new_user(user_id)
        user_step = 0
        user_info = (0, False, False, False)

        if len(message.text) > 7:
            ref_code = message.text[8:]
            try:
                u_id, count = db.get_referral_code_info(ref_code)
                if u_id != user_id:
                    db.set_user_referral_code(user_id,u_id)
                    count += 1
                    db.set_referral_code_user_count(u_id, count)
                    if count % 5 == 0 and count != 0:
                        count = db.get_manual_ups(u_id) + 1
                        db.set_manual_ups(u_id, count)

            except Exception:
                tb.send_message(chat_id, 'Неверный код')

    else:
        user_step = user_info[0]

    ban, status = user_info[1:3]

    if ban:
        if status:
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
    chat_id = message.chat.id
    user_info = db.get_user_step_ban_status_is_admin(user_id)

    if len(user_info) == 0:
        adding_new_user(user_id)
        user_step = 0
        user_info = (0, False, False, False)
    else:
        user_step = user_info[0]

    ban, status = user_info[1:3]

    if ban:
        if status:
            db.set_notified_ban_status(user_id, True)
            mes.text_message(chat_id,
                             "К сожалению вы заблокированы админиистрацией")
            return

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return
        mes.help_nm(message.chat.id, user_info[3])
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
    user_info = db.get_user_step_ban_status_is_admin(user_id)

    if len(user_info) == 0:
        adding_new_user(user_id)
        user_step = 0
        user_info = (0, False, False, False)
    else:
        user_step = user_info[0]

    ban, status = user_info[1:3]

    if ban:
        if status:
            db.set_notified_ban_status(user_id, True)
            mes.text_message(chat_id,
                             "К сожалению вы заблокированы "
                             "админиистрацией")
            return
        if not status:
            db.set_notified_ban_status(user_id, True)
            mes.text_message(chat_id,
                             "К сожалению вы заблокированы админиистрацией")
            return

    # Handle command

    call_data_lowered = call.data.lower()
    if call_data_lowered == "noanswer":
        return

    if call.message.chat.type == "private":
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
                mes.categories_post(chat_id, message_id, user_id,
                                    post_type=1)
                return

            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_CREATECUSTOMERPOST:
                    return
                db.set_prepare_user_post_type(user_id, 2)
                mes.categories_post(chat_id, message_id, user_id,
                                    post_type=2)

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

                categories = categories_str.split(":")

                for index in range(1, len(categories)):
                    ans = db.get_category_parent_if_exists(categories[index])
                    if not len(ans) or int(categories[index - 1]) != ans[0]:
                        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                        keyboard.add(
                            telebot.types.InlineKeyboardButton(text="Ошибка ❌",
                                                               callback_data="noAnswer"))
                        tb.edit_message_text(
                            text="Что-то пошло не так",
                            chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
                        db.set_prepare_user_categories(user_id, "")
                        mes.categories_post(chat_id, message_id, user_id, post_type)
                        return

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
                    mes.categories_post(chat_id, message_id, user_id,
                                        post_type)

                elif len(categories_str) == 0:
                    mes.side_menu(chat_id, message_id, user_id)

                else:
                    ind = len(categories_str) - 2
                    category_to_show = categories_str[ind]

                    categories_str = categories_str[:ind + 1]
                    db.set_prepare_user_categories(user_id,
                                                   ';'.join(categories_str))
                    mes.subcategories_post(chat_id, message_id,
                                           category_to_show, user_id,
                                           post_type)
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
                ans = bool(int(ans))
            except ValueError or KeyError:
                mes.text_message(chat_id, "Неверный вариант")
                return

            db.set_prepare_user_guarantee(user_id, ans)
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            if ans:
                keyboard.add(telebot.types.InlineKeyboardButton(text="Да ✅", callback_data="noAnswer"))
            else:
                keyboard.add(telebot.types.InlineKeyboardButton(text="Нет ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=chat_id,
                                         message_id=message_id,
                                         reply_markup=keyboard)
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
                actual_post_type = db.get_prepare_post_type(user_id)[0]
                if actual_post_type == 2:
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(text="Ошибка ❌",
                                                           callback_data="noAnswer"))
                    tb.edit_message_text(
                        text="Что-то пошло не так",
                        chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
                    mes.set_portfolio_customer_post_nm(chat_id, user_id)
                    return
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

        elif call_data_lowered[:12] == "preview_post":
            post_type = (1 if call_data_lowered[13:15] == "fr" else 2)
            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_PREVIEW_POST_FR:
                    return
            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_PREVIEW_POST_CU:
                    return

            left_part = call_data_lowered[16:]
            if left_part == "bm":
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text="Назад ✅", callback_data="noAnswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

            mes.send_prepared_post(chat_id, message_id, user_id)
            return

        elif call_data_lowered[:8] == "postpage":
            page = call_data_lowered[9:]
            try:
                page = int(page)
            except ValueError:
                mes.text_message(chat_id, "Нет такой страницы")
                return

            mes.send_posts_page(chat_id, message_id, user_id, page)
            return

        elif call_data_lowered[:4] == "post":
            post_type = (1 if call_data_lowered[5:7] == "fr" else 2)
            if post_type == 1:
                if user_step not in POSSIBLE_COME_TO_POST_FR:
                    return
            elif post_type == 2:
                if user_step not in POSSIBLE_COME_TO_POST_CU:
                    return
            all_post = [str(i) for i in db.get_prepare_post_all(user_id)]
            new_post_id = random.randint(1, 1000000)
            while bool(db.is_post_id_exist(new_post_id)):
                new_post_id = random.randint(1, 1000000)

            creation_date = int(time.time())
            db.add_post(new_post_id, user_id, creation_date, creation_date,
                        *all_post)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(
                text="Опубликовать ✅", callback_data="noAnswer"))
            tb.edit_message_reply_markup(chat_id=chat_id,
                                         message_id=message_id,
                                         reply_markup=keyboard)
            count = db.get_user_posts_count(user_id)[0]
            count += 1
            db.set_user_posts_count(user_id, count)
            mes.send_post(ID_POST_CHANNEL, new_post_id)
            mes.posted(chat_id, user_id, new_post_id)
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

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(text="К редактированию ✅",
                                                                callback_data="noAnswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)
                mes.edit_pbp_menu_nm(chat_id, user_id, post_type)
                return

            elif left_part[:10] == "categories":
                post_type = (1 if left_part[11:13] == "fr" else 2)

                if left_part[14] == "n":
                    if post_type == 1:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_FR:
                            return
                    elif post_type == 2:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_CU:
                            return

                    parent_category_id = left_part[16:]
                    if not len(db.is_category_exist(parent_category_id)):
                        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                        keyboard.add(
                            telebot.types.InlineKeyboardButton(text="Ошибка ❌",
                                                               callback_data="noAnswer"))
                        tb.edit_message_text(text="Неизвестная категория. Возможно она была удалена",
                                             chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
                        db.set_prepare_new_user_categories(user_id, "")
                        mes.edit_pbp_menu(chat_id, message_id, user_id, post_type)
                        return

                    category_children = db.get_category_children_if_exists(
                        parent_category_id)

                    categories_str = db.get_prepare_new_user_categories(user_id)[0]
                    if parent_category_id == "0":
                        categories_str = ""
                    elif categories_str:
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

                    categories = categories_str.split(":")

                    for index in range(1, len(categories)):
                        ans = db.get_category_parent_if_exists(categories[index])
                        if not len(ans) or int(categories[index - 1]) != ans[0]:
                            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                            keyboard.add(
                                telebot.types.InlineKeyboardButton(text="Ошибка ❌",
                                                                   callback_data="noAnswer"))
                            tb.edit_message_text(
                                text="Что-то пошло не так",
                                chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
                            db.set_prepare_new_user_categories(user_id, "")
                            mes.send_prepared_post_nm(chat_id, user_id)
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

                elif left_part[14] == "b":
                    if post_type == 1:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_BACK_FR:
                            return
                    elif post_type == 2:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_BACK_CU:
                            return

                    categories_str = db.get_prepare_new_user_categories(user_id)[0].split(";")

                    # if len(categories_str) == 1:
                    #     db.set_prepare_new_user_categories(user_id, "")
                    #     mes.categories_post(chat_id, message_id, user_id,
                    #                         post_type)
                    if len(categories_str) == 0:
                        mes.edit_pbp_menu(chat_id, message_id, user_id, post_type)
                    elif len(categories_str) == 1:
                        db.set_prepare_new_user_categories(user_id, "")
                        mes.edit_pbp_categories(chat_id, message_id, "0", user_id, post_type)
                        return
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

            elif left_part[:5] == "title":
                post_type = (1 if left_part[6:8] == "fr" else 2)
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_TITLE_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_TITLE_CU:
                        return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text="Название ✅", callback_data="noAnswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)
                mes.edit_pbp_title_nm(chat_id, user_id, post_type)
                return

            elif left_part[:11] == "description":
                post_type = (1 if left_part[12:14] == "fr" else 2)
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_DESCRIPTION_FR:
                        return
                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_DESCRIPTION_CU:
                        return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text="Описание ✅", callback_data="noAnswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)
                mes.edit_pbp_description_nm(chat_id, user_id, post_type)
                return

            elif left_part[:4] == "memo":
                if user_step not in POSSIBLE_COME_TO_EDIT_PBP_MEMO:
                    return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text="Памятку ✅", callback_data="noAnswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)
                mes.edit_pbp_memo_nm(chat_id, user_id)
                return

            elif left_part[:9] == "portfolio":
                post_type = (1 if left_part[10:12] == "fr" else 2)

                if post_type == 1:
                    left_part_another = left_part[13:]
                    if len(left_part_another) > 0 and left_part_another[0] == 'n':
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_NO_PORTFOLIO_FR:
                            return
                        actual_post_type = db.get_prepare_post_type(user_id)
                        if actual_post_type == 2:
                            mes.text_message( text="Что-то пошло не так", chat_id=chat_id)
                            mes.edit_pbp_portfolio(chat_id, message_id, user_id)
                            return

                        db.set_prepare_user_portfolio(user_id, "")
                        keyboard = telebot.types.InlineKeyboardMarkup(
                            row_width=1)
                        keyboard.add(telebot.types.InlineKeyboardButton(
                            text="Нет портфолио ✅", callback_data="noAnswer"))
                        tb.edit_message_reply_markup(chat_id=chat_id,
                                                     message_id=message_id,
                                                     reply_markup=keyboard)
                        mes.send_prepared_post_nm(chat_id, user_id)
                        return

                    else:
                        if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PORTFOLIO_FR:
                            return

                        keyboard = telebot.types.InlineKeyboardMarkup(
                            row_width=1)
                        keyboard.add(telebot.types.InlineKeyboardButton(
                            text="Портфолио ✅", callback_data="noAnswer"))
                        tb.edit_message_reply_markup(chat_id=chat_id,
                                                     message_id=message_id,
                                                     reply_markup=keyboard)
                        mes.edit_pbp_portfolio_nm(chat_id, user_id)
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PORTFOLIO_CU:
                        return

                    left_part_another = left_part[13:]

                    if len(left_part_another) == 0:
                        keyboard = telebot.types.InlineKeyboardMarkup(
                            row_width=1)
                        keyboard.add(
                            telebot.types.InlineKeyboardButton(
                                text="Портфолио ✅",
                                callback_data="noanswer"))

                        # Удаляем предыдущую клавиатуру
                        tb.edit_message_reply_markup(chat_id=chat_id,
                                                     message_id=message_id,
                                                     reply_markup=keyboard)
                        db.set_prepare_user_portfolio(user_id, "1")
                        mes.edit_pbp_portfolio(chat_id, message_id, user_id)
                        return

                    try:
                        ans = bool(int(left_part_another))
                    except ValueError:
                        return

                    if ans:
                        keyboard = telebot.types.InlineKeyboardMarkup(
                            row_width=1)
                        keyboard.add(
                            telebot.types.InlineKeyboardButton(
                                text="Да ✅",
                                callback_data="noanswer"))

                        # Удаляем предыдущую клавиатуру
                        tb.edit_message_reply_markup(chat_id=chat_id,
                                                     message_id=message_id,
                                                     reply_markup=keyboard)
                        db.set_prepare_user_portfolio(user_id, "1")
                    else:
                        keyboard = telebot.types.InlineKeyboardMarkup(
                            row_width=1)
                        keyboard.add(
                            telebot.types.InlineKeyboardButton(
                                text="Нет ✅",
                                callback_data="noanswer"))

                        # Удаляем предыдущую клавиатуру
                        tb.edit_message_reply_markup(chat_id=chat_id,
                                                     message_id=message_id,
                                                     reply_markup=keyboard)
                        db.set_prepare_user_portfolio(user_id, "")

                    mes.send_prepared_post_nm(chat_id, user_id)
                    return

            elif left_part[:8] == "contacts":
                post_type = (1 if left_part[9:11] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_CONTACTS_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_CONTACTS_CU:
                        return

                keyboard = telebot.types.InlineKeyboardMarkup(
                    row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton(
                    text="Контакты ✅", callback_data="noAnswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)
                mes.edit_pbp_contacts_nm(chat_id, user_id, post_type)
                return

            elif left_part[:12] == "payment_type":
                post_type = (1 if left_part[13:15] == "fr" else 2)
                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENTTYPE_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENTTYPE_CU:
                        return

                pay_data = left_part[16:]

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
                    db.set_prepare_user_payment_type(user_id, 1)
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

            elif left_part[:7] == "payment":
                post_type = (1 if left_part[8:10] == "fr" else 2)

                if post_type == 1:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENT_FR:
                        return

                elif post_type == 2:
                    if user_step not in POSSIBLE_COME_TO_EDIT_PBP_PAYMENT_CU:
                        return

                mes.edit_pbp_payment_menu(chat_id, message_id, user_id)
                return

            elif left_part[:5] == "price":
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

            elif left_part[:7] == "price_2":
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

            elif left_part[:9] == "guarantee":
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
                    keyboard = telebot.types.InlineKeyboardMarkup(
                        row_width=1)
                    keyboard.add(telebot.types.InlineKeyboardButton(
                        text="Да ✅", callback_data="noAnswer"))
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)
                    mes.send_prepared_post_nm(chat_id, user_id)
                    return

                elif left_part_another == "n":
                    db.set_prepare_user_guarantee(user_id, False)
                    keyboard = telebot.types.InlineKeyboardMarkup(
                        row_width=1)
                    keyboard.add(telebot.types.InlineKeyboardButton(
                        text="Нет ✅", callback_data="noAnswer"))
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)
                    mes.send_prepared_post_nm(chat_id, user_id)
                    return

                mes.edit_pbp_guarantee(chat_id, message_id, user_id, post_type)
                return

        elif call_data_lowered[:3] == "get":
            post_id = call_data_lowered[4:]

            try:
                post_id = str(post_id)
            except ValueError:
                return

            ans = db.get_post_owner_id_if_exists(post_id)
            if not len(ans):
                mes.text_message(chat_id, "Объявления с таким id не существует")
                return

            if ans[0] != user_id:
                mes.text_message(chat_id, "Нельзя посмотреть чужое объявление")
                return

            mes.get_post_nm(chat_id, post_id)
            return

        elif call_data_lowered[:12] == "verification":

            left_part = call_data_lowered[13:]
            if user_step not in POSSIBLE_COME_TO_VERIFICATION_TICKET:
                return

            if left_part == "1":
                mes.send_verification_ticket(chat_id, message_id, user_id, page=1)
                return

            elif left_part == "2":
                mes.send_verification_ticket(chat_id, message_id, user_id, page=2)
                return

            elif left_part == "new_ticket":
                status = db.get_verification_ticket_status(user_id)[0]

                if (status >> 7 & 1):
                    mes.verified_by_admin(chat_id, message_id)
                    return

                if (status >> 5 & 1) and not (status >> 6 & 1):
                    db.set_verification_ticket(user_id, "", "", "0")
                    mes.send_verification_ticket(chat_id, message_id, user_id, page=1)
                    return
                else:
                    mes.text_message(chat_id, T_HELP_VERIFICATION_EDIT)

                return

            elif left_part[:4] == "edit":

                if len(left_part) < 5:
                    return

                if (status >> 7 & 1):
                    mes.verified_by_admin(chat_id, message_id)
                    return

                if left_part[5] == "1":
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(telebot.types.InlineKeyboardButton(text="Редактировать описание ✅",
                                                                    callback_data="noAnswer"))
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)
                    mes.enter_verification_text_nm(chat_id, user_id)
                    return

                elif left_part[5] == "2":
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                    keyboard.add(telebot.types.InlineKeyboardButton(text="Редактировать контакты ✅",
                                                                    callback_data="noAnswer"))
                    tb.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=keyboard)
                    mes.enter_verification_contacts_nm(chat_id, user_id)
                    return

                return

            elif left_part == "pay":
                status = db.get_verification_ticket_status(user_id)[0]

                if (status >> 7 & 1):
                    mes.verified_by_admin(chat_id, message_id)
                    return

                if (status >> 3 & 1):
                    mes.text_message(chat_id, "Вы уже все оплатили")
                    return

                if (status >> 4 & 1):
                    mes.text_message(chat_id, "Ошибка")
                    return
                #
                # keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                # keyboard.add(telebot.types.InlineKeyboardButton(text="Оплата ✅",
                #                                                 callback_data="noAnswer"))
                # tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)

                mes.pay_verification(chat_id, user_id)
                return

            elif left_part == "send":
                status = db.get_verification_ticket_status(user_id)[0]

                if (status >> 7 & 1):
                    mes.verified_by_admin(chat_id, message_id)
                    return

                if (status >> 3 & 1) and (status >> 2 & 1) and (status >> 1 & 1):
                    status = (status | (1 << 4))
                    db.set_verification_ticket_status(user_id, status)
                    mes.send_verification_ticket(chat_id, message_id, user_id, page=1)
                    mes.send_approve_verification_ticket_nm(ID_MANAGE_CHANNEL, user_id)
                    mes.text_message(chat_id, "Отправлено")
                    return

                mes.text_message(chat_id, "Рано отправлять")
                return

            elif left_part == "cancel":
                status = db.get_verification_ticket_status(user_id)[0]

                if (status >> 7 & 1):
                    mes.verified_by_admin(chat_id, message_id)
                    return

                if (status >> 4 & 1) and not (status >> 5 & 1):
                    status = (status ^ (1 << 4))
                    db.set_verification_ticket_status(user_id, status)
                    mes.send_verification_ticket(chat_id, message_id, user_id, page=1)
                    return

                mes.text_message(chat_id, "Нечего отменять")
                return

            return

        elif call_data_lowered[:10] == "buying_ups":
            left_part = call_data_lowered[11:]

            if left_part[:4] == "menu":
                if user_step not in POSSIBLE_COME_TO_BUYING_UPS_MENU:
                    return

                try:
                    post_id = int(left_part[5:])
                except ValueError:
                    return

                mes.buying_ups_menu(chat_id, message_id,
                                     user_id, post_id)
                return

            elif left_part[:4] == "auto":
                if user_step not in POSSIBLE_COME_TO_BUYING_AUTO_UPS:
                    return

                try:
                    post_id = int(left_part[5:])
                except ValueError:
                    return

                if db.get_post_rate(post_id)[0] != 0:
                    mes.post_has_auto_ups(chat_id, message_id, post_id)
                    return

                mes.available_auto_rates(chat_id, message_id,
                                         user_id, post_id)
                return

            elif left_part[:6] == "manual":
                if user_step not in POSSIBLE_COME_TO_BUYING_MANUAL_UPS:
                    return

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton("Ручные подъемы ✅",
                    callback_data="noanswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

                mes.enter_manual_ups_nm(chat_id, user_id)
                return

            elif left_part[:4] == "rate":
                if user_step not in POSSIBLE_COME_TO_RATES_UPS_MENU:
                    return

                try:
                    left_part = left_part[5:]
                    if not left_part.count("_"):
                        raise ValueError

                    index = left_part.index("_")
                    post_id = int(left_part[:index])
                    rate_id = int(left_part[index + 1:])

                except ValueError:
                    mes.text_message(chat_id, "Ошибка")
                    return

                if db.get_post_rate(post_id)[0] != 0:
                    mes.post_has_auto_ups(chat_id, message_id, post_id)
                    return

                rate_info = db.get_rate_time_and_price_if_exist(rate_id)
                if not len(rate_info):
                    mes.text_message(chat_id, "Такого тарифа не существует")
                    return

                update_time, price = rate_info

                db.set_user_chose_rate_and_post_to(user_id, rate_id, post_id)

                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(telebot.types.InlineKeyboardButton("1 раз в " +
                                                                mes.nice_time(update_time) +
                                                                " (" + str(price) + " р.) ✅",
                                                                callback_data="noanswer"))
                tb.edit_message_reply_markup(chat_id=chat_id,
                                             message_id=message_id,
                                             reply_markup=keyboard)

                mes.enter_auto_ups(chat_id, user_id)
                return

            return

        elif call_data_lowered[:2] == "up":
            post_id = call_data_lowered[3:]

            try:
                post_id = int(post_id)
            except ValueError:
                return

            ans = db.get_post_owner_id_and_last_up_and_rate_id_if_exists(post_id)
            if not len(ans):
                mes.text_message(chat_id, "Объявления с таким id не существует")
                return

            if ans[0] != user_id:
                mes.text_message(chat_id, "Нельзя поднять чужое объявление")
                return

            if int(time.time()) - 10800 < ans[1]:
                mes.text_message(chat_id, "Еще рано поднимать объявление. Осталось " + mes.nice_time(ans[1] + 10800 - int(time.time())))
                return

            manual_ups = db.get_user_manual_ups(user_id)[0]
            if manual_ups == 0:
                mes.no_manual_ups_nm(chat_id, post_id)
                return

            manual_ups -= 1
            t = int(time.time())
            db.set_manual_ups(user_id, manual_ups)
            db.set_post_last_up(post_id, t)
            if ans[2]:
                update_time = db.get_rate_time(ans[2])[0]
                db.set_time_to_do_auto_post(post_id, t + update_time)

            mes.send_post(ID_POST_CHANNEL, post_id)
            mes.get_post(chat_id, message_id, post_id)
            return
        #
        # elif call_data_lowered[:8] == "getpost":
        #
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
        return


@tb.message_handler()
def all_left_text_messages(message: telebot.types.Message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(
            message.chat.id) + " " + message.text + "\n")

    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id

    user_info = db.get_user_step_ban_status_is_admin(user_id)

    if len(user_info) == 0:
        adding_new_user(user_id)
        user_step = 0
        user_info = (0, False, False, False)
    else:
        user_step = user_info[0]

    if message.chat.type == 'private':
        if user_step == 29:
            mes.text_message(message, T_COMPLETE_EDITING)
            return

        lowered_message = message.text.lower()

        ans = handle_common_command(lowered_message, chat_id, user_id)
        if ans:
            return

        if user_info[3]:  # ADMIN STATUS
            ans = handle_admin_command(lowered_message, chat_id, user_id)
            if ans:
                return

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
                mes.edit_pbp_range_price_1_nm(chat_id, user_id)
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

            elif user_step == 151:
                mes.send_verification_ticket_nm(chat_id, user_id, page=1)
                return

            elif user_step == 152:
                mes.send_verification_ticket_nm(chat_id, user_id, page=1)
                return

            elif user_step == 153:
                mes.send_verification_ticket_nm(chat_id, user_id, page=1)
                return

            elif user_step == 160:
                mes.send_posts_page_nm(chat_id, user_id, 1)
                return

            elif user_step == 161:
                mes.send_posts_page_nm(chat_id, user_id, 1)
                return

            elif user_step == 162:
                mes.send_posts_page_nm(chat_id, user_id, 1)
                return

            elif user_step == 163:
                mes.send_posts_page_nm(chat_id, user_id, 1)
                return

            elif user_step == 164:
                mes.send_posts_page_nm(chat_id, user_id, 1)
                return

            elif user_step == 165:
                mes.send_posts_page_nm(chat_id, user_id, 1)
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
                    mes.edit_pbp_range_price_2_nm(chat_id, user_id, 1)
                else:
                    mes.edit_pbp_range_price_2_nm(chat_id, user_id, 2)
                return

            elif user_step in (26, 119):

                price1 = db.get_prepare_new_user_price(user_id)[0]
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

            elif user_step == 151:
                ans, error_text = is_suitable_about_verification(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_verification_text(user_id, message.text)
                status = db.get_verification_ticket_status(user_id)[0]
                status = (status | (1 << 1))
                db.set_verification_ticket_status(user_id, status)
                mes.send_verification_ticket_nm(chat_id, user_id, page=1)
                return

            elif user_step == 152:
                ans, error_text = is_suitable_links_verification(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                db.set_verification_contacts(user_id, message.text)
                status = db.get_verification_ticket_status(user_id)[0]
                status = (status | (1 << 2))
                db.set_verification_ticket_status(user_id, status)
                mes.send_verification_ticket_nm(chat_id, user_id, page=2)
                return

            elif user_step == 153:
                return

            elif user_step == 160:
                return

            elif user_step == 161:
                ans, error_text = is_suitable_ups_count(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return

                mes.send_invoice_manual_ups(chat_id, user_id, int(message.text))
                return

            elif user_step == 162:
                return

            elif user_step == 163:
                ans, error_text = is_suitable_ups_count(message.text)
                if not ans:
                    mes.text_message(chat_id, error_text)
                    return
                rate_id, post_id = db.get_user_chose_rate_and_post_to(user_id)
                post_owner_id = db.get_post_owner_id_if_exists(post_id)
                if not len(post_owner_id):
                    mes.text_message(chat_id, "Такого объявления не существует")
                    return

                post_owner_id = post_owner_id[0]
                if post_owner_id != user_id:
                    mes.text_message(chat_id, "Это не ваше объявление")
                    return

                price = db.get_rate_price_if_exist(rate_id)
                if not len(price):
                    mes.text_message(chat_id, "Такого тарифа не существует")
                    return

                price = price[0]

                mes.send_auto_ups_invoice(chat_id, user_id, post_id,
                                          rate_id, price, int(message.text))
                return

            elif user_step == 164:
                return

            elif user_step == 165:
                return

    elif message.chat.type == 'group':

        lowered_message = message.text.lower()
        ans = handle_common_command(lowered_message, chat_id, user_id)
        if ans:
            return

        if user_info[3]:  # ADMIN STATUS
            ans = handle_admin_command(lowered_message, chat_id, user_id,
                                       chat_type=2)
            if ans:
                return


@tb.pre_checkout_query_handler(func=lambda query: True)
def check(pre_checkout_query):
    user_id = pre_checkout_query.from_user.id
    user_info = db.get_user_step_ban_status_is_admin(user_id)
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ERROR PAYMENT",
                              time.gmtime(time.time())) + str(
                              user_id) + " " + str(
                              pre_checkout_query.id) + "\n")

    if len(user_info) == 0:
        adding_new_user(user_id)
        user_step = 0
        user_info = (0, False, False, False)
    else:
        user_step = user_info[0]

    ban, status = user_info[1:3]

    if ban:
        return

    tb.answer_pre_checkout_query(pre_checkout_query.id,
                                 ok=True, error_message="Ошибка")


@tb.message_handler(content_types=['successful_payment'])
def got_payment(message):
    with open(P_ACTIONS, "a") as f:
        f.write(time.strftime("[%H:%M:%S %d.%m.%Y] ",
                              time.gmtime(time.time())) + str(
            message.chat.id) + " " + message.successful_payment.invoice_payload + "\n")
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_info = db.get_user_step_ban_status_is_admin(user_id)
    invoice_payload = message.successful_payment.invoice_payload

    if len(user_info) == 0:
        adding_new_user(user_id)
        user_step = 0
        user_info = (0, False, False, False)
    else:
        user_step = user_info[0]

    ban, status = user_info[1:3]

    if ban:
        if status:
            db.set_notified_ban_status(user_id, True)
            mes.text_message(chat_id,
                             "К сожалению вы заблокированы админиистрацией")
            return

    if invoice_payload == "201":
        status = db.get_verification_ticket_status(user_id)[0]

        status = (status | (1 << 3))
        db.set_verification_ticket_status(user_id, status)

        mes.verification_paid(chat_id)
        mes.send_verification_ticket_nm(chat_id, user_id, page=1)
        return

    elif invoice_payload[:3] == "202":
        invoice_payload = invoice_payload[4:]
        try:
            ups = int(invoice_payload)
        except ValueError:
            mes.text_message(chat_id, "Ошибка")
            return

        manual_ups = db.get_user_manual_ups(user_id)[0]
        manual_ups += ups
        db.set_manual_ups(user_id, manual_ups)
        mes.text_message(chat_id, "Успешная покупка. "
                                  "Теперь у вас " + str(
                                   manual_ups) + " подъемов.")
        return

    elif invoice_payload[:3] == "203":
        try:
            invoice_payload = invoice_payload[4:]
            index = invoice_payload.index(":")
            index2 = invoice_payload.index("=")
            rate_id = int(invoice_payload[:index])
            post_id = int(invoice_payload[index + 1:index2])
            ups = int(invoice_payload[index2 + 1:])
            print(rate_id, post_id, ups)
        except ValueError:
            mes.text_message(chat_id, "Ошибка")
            return

        rate_info = db.get_rate_time_if_exist(rate_id)
        if len(rate_info) == 0:
            mes.text_message(chat_id, "Ошибка")
            return

        post_info = db.get_post_owner_id_if_exists(post_id)
        if len(post_info) == 0 or post_info[0] != user_id:
            mes.text_message(chat_id, "Ошибка")
            return

        update_time = rate_info[0]
        db.set_post_auto_ups_info(post_id, rate_id, ups)
        db.add_auto_actions_task(1, int(time.time()) + update_time,
                              post_id, update_time, rate_id,
                              maxcount=ups)

        mes.text_message(chat_id, "Успешная покупка. Теперь объявление будет "
                                  "автоматически публиковаться "
                                  "раз в " + mes.nice_time(update_time))
        return
    return


#
def handle_common_command(command: str, chat_id: str or int, user_id: str or int):
    if command[:8] == "/myposts":
        left_part = command[9:]
        try:
            page = int(left_part)
            if page < 1:
                raise ValueError
        except ValueError:
            mes.text_message(chat_id, "Формат команды /myposts Число")
            return True

        mes.send_posts_page_nm(chat_id, user_id, page)
        return True

    elif command[:10] == "/open_post":
        left_part = command[11:]
        try:
            post_id = int(left_part)
        except ValueError:
            mes.text_message(chat_id, "Формат команды /open_post Число")
            return True

        ans = db.get_post_owner_id_if_exists(post_id)
        if not len(ans) or ans[0] != int(user_id):
            mes.text_message(chat_id, "Ошибка доступа")
            return True

        mes.get_post_nm(chat_id, post_id)
        return True

    # TODO  reports bot
    # elif command[:7] == "/report":
    #     left_part = command[8:]
    #     try:
    #         post_id = int(left_part)
    #     except ValueError:
    #         return
    #
    #     ans = db.get_user_report_if_exist(user_id, post_id)
    #     if len(ans):
    #         mes.text_message(chat_id, "Вы уже жаловались на это объявление")
    #         return
    #
    #     reports = ans.get_post_reports(post_id)
    #     reports += 1
    #     db.add_user_report(user_id, post_id)
    #
    #     if are_reports_enough(reports):
    #         db.set_post_reports_and_sent_status(post_id, reports, True)
    #         mes.send_report_ticket(ID_MANAGE_CHANNEL, post_id)
    #         return
    #
    #     db.set_post_reports(post_id, reports)
    #     mes.text_message(chat_id, "Ваша жалоба отправлена")
    #     return
    #
    # elif command[:14] == "/cancel_report":
    #     left_part = command[15:]
    #     try:
    #         post_id = int(left_part)
    #     except ValueError:
    #         return
    #
    #     ans = db.get_user_report_if_exist(user_id, post_id)
    #     if not len(ans):
    #         mes.text_message(chat_id, "Вы ещё не жаловались на это объявление")
    #         return
    #
    #     reports = ans.get_post_reports(post_id)
    #     reports -= 1
    #     db.del_user_report(user_id, post_id)
    #     db.set_post_reports(post_id, reports)
    #     mes.text_message(chat_id, "Ваша жалоба отменена")
    #     return


#
def handle_admin_command(command: str, chat_id: str or int, user_id: str or int, chat_type=1):
    try:
        if str(command[:9]) == '/unverify':
            try:
                user_id_to_unverify = command[10:]
                if user_id_to_unverify[-1] == "]":
                    user_id_to_unverify = user_id_to_unverify[:-1]

                user_id_to_unverify = int(user_id_to_unverify)

            except ValueError:
                mes.text_message(chat_id, "Неверный формат id")
                return True

            db.set_user_verification_status(user_id_to_unverify, False)
            status = db.get_user_verification_status(user_id_to_unverify)[0]
            db.set_verification_ticket_status(user_id_to_unverify, status & 63)
            mes.text_message(chat_id,
                             "Если пользователь с таким ID существует, то его данные обновлены")
            return True

        elif command[:7] == "/verify":
            try:
                user_id_to_verify = command[8:]
                if user_id_to_verify[-1] == "]":
                    user_id_to_verify = user_id_to_verify[:-1]

                user_id_to_verify = int(user_id_to_verify)
            except ValueError:
                mes.text_message(chat_id, "Неверный формат id")
                return True

            status = db.get_user_verification_status(user_id_to_verify)[0]
            db.set_user_verification_status(user_id_to_verify, True)
            db.set_verification_ticket_status(user_id_to_verify, status | 128)
            mes.text_message(chat_id,
                             "Если пользователь с таким ID существует, то его данные обновлены")
            return True

        elif command[:10] == "/user_info":

            try:
                user_id_to_info= command[11:]

                user_id_to_info = user_id_to_info[:-1]
                user_id_to_info = int(user_id_to_info)
                info = db.get_user_info(user_id_to_info)
                sms = 'ID пользователя: ' + str(info[0]) + '\n'
                sms += 'Постов у юзера: ' + str(info[1]) + '\n'
                sms += 'Ручных апов: ' + str(info[2]) + '\n'
                sms += 'Потрачено денег: : ' + str(info[3]) + ' руб' + '\n'
                sms += 'Верифицирован: ' + str(info[4]) + '\n'
                sms += 'Наличие бана: ' + str(info[7]) + '\n'
                mes.text_message(chat_id, sms)
            except ValueError:
                mes.text_message(chat_id, "Неверный формат id")
                return True
            return True

        elif command[:9] == "/ban_user":
            try:
                user_id_to_ban = command[10:]

                user_id_to_ban = user_id_to_ban[:-1]
                user_id_to_ban = int(user_id_to_ban)
                db.set_ban_status(True,user_id_to_ban)
                mes.text_message(chat_id,
                                 "Пользователь успешно забанен, его объявления удалены, автоподьемы обнулены, доступ к платформе заблокирован ")
            except ValueError:
                mes.text_message(chat_id, "Неверный формат id")
                return True

            return True

        elif command[:12] == "/delete_user":
            return True

        elif command[:11] == "/user_posts":
            return True

        elif command[:10] == "/hide_rate":
            return True

        elif command[:12] == "/delete_rate":
            return True

        elif command[:12] == "/create_rate":
            return True

        elif command[:10] == "/show_rate":
            return True

        elif command[:18] == "/set_referral_code":
            # До 30 символов! (включительно)
            try:
                user_id_to_ref = command[19:]
                i = 0
                while user_id_to_ref[i]!=']':
                    i +=1
                code = user_id_to_ref[i+2:len(user_id_to_ref)-1]
                user_id_to_ref = user_id_to_ref[:i]
                user_id_to_ref = int(user_id_to_ref)
                print(code)
                print(user_id_to_ref)

                db.set_referral_code(code, user_id)
                mes.text_message(chat_id,
                                 "Пользователю успешно присвоен реферальный код ")
            except ValueError:
                mes.text_message(chat_id, "Неверный формат id")
                return True

            return True

        elif command[:11] == "/list_posts":
            return True

        elif command[:12] == "/delete_post":
            return True

        elif command[:10] == "/post_info":
            try:
                post_info = command[13:]
                post_info = post_info[:-1]
                post_info = int(post_info)
                info = db.get_post_all(post_info)
                sms = 'Тип обьявления: ' + str(info[0]) + '\n'
                sms += 'Загаловок: ' + str(info[1]) + '\n'
                sms += 'Дата создания: ' + str(info[10]) + '\n'
                sms += 'Последний подъём: ' + str(info[11]) + ' руб' + '\n'
                sms += 'Id создателя: ' + str(info[14]) + '\n'
                sms += 'Сколько автоподъёмов использовано: ' + str(info[13]) + '\n'
                sms += 'Сколько автоподъёмов осталось исполнить: ' + str(info[12]) + '\n'
                mes.text_message(chat_id, sms)
            except ValueError:
                mes.text_message(chat_id, "Неверный формат id")
                return True
            return True

        elif command[:12] == "/clear_cache":
            return True

        elif command[:10] == "/add_admin":
            left_part = command[11:]

            try:
                admin_id = int(left_part)
            except ValueError:
                mes.text_message(chat_id, "Формат команды "
                                          "/add_admin_АЙдиПользователя")
                return True

            db.set_admin_status(admin_id, True)
            mes.text_message(chat_id,
                             "Если такой пользователь существует, "
                             "то он был назначен Администратором")
            return True

        elif command[:10] == "/del_admin":
            left_part = command[11:]

            try:
                admin_id = int(left_part)
            except ValueError:
                mes.text_message(chat_id, "Формат команды /add_admin_АЙдиПользователя")
                return True

            db.set_admin_status(admin_id)
            mes.text_message(chat_id, "Если такой пользователь есть, то он перестал быть Администратором")
            return True

        elif command[:9] == "/commands":
            mes.text_message(chat_id, T_COMMANDS_LIST)
            return True

        if chat_type == 2:

            if command[:10] == "/approve_v":
                left_part = command[11:]

                try:
                    user_id_to_act = int(left_part)
                except ValueError:
                    mes.text_message(chat_id, "Команда введена неверно. "
                                              "Неудается получить id пользователя")
                    return True
                status = db.get_verification_ticket_status(user_id_to_act)[0]

                if (status >> 7 & 1):
                    mes.text_message(chat_id, "Пользователь был верифицирован "
                                              "лично администрацией. "
                                              "(Через команду /verify)")
                    return

                if not (status >> 4 & 1):
                    mes.text_message(chat_id, "Действие невозможно выполнить. "
                                              "Пользователь отменил заявку "
                                              "или ещё не отправлял её")
                    return

                if (status >> 5 & 1):
                    if (status >> 6 & 1):
                        mes.text_message(chat_id, "Пользователь уже верифицирован")
                    else:
                        mes.text_message(chat_id, "Пользователь не верифицирован. "
                                                  "Последняя его заявка была "
                                                  "отклонена, а новых он не отправлял")
                    return

                db.set_verification_status(user_id_to_act, True)
                status = (status | (1 << 5) | (1 << 6))
                db.set_verification_ticket_status(user_id, status)
                mes.text_message(chat_id, str(user_id_to_act)
                                 + " теперь верифицирован!")
                return

            elif command[:7] == "/deny_v":
                left_part = command[8:]

                try:
                    user_id_to_act = int(left_part)
                except ValueError:
                    mes.text_message(chat_id, "Команда введена неверно. "
                                              "Неудается получить id пользователя")
                    return True
                status = db.get_verification_ticket_status(user_id_to_act)[0]
                if not (status >> 4 & 1):
                    mes.text_message(chat_id, "Действие невозможно выполнить. "
                                              "У пользователя нет ожидающих проверки запросов на верификацию")
                    return

                if (status >> 5 & 1):
                    mes.text_message(chat_id, "Пользователь не отправлял"
                                              " новых заявок с прошлого раза")
                    return

                db.set_verification_status(user_id_to_act, True)
                status = (status | (1 << 5))
                db.set_verification_ticket_status(user_id, status)
                mes.text_message(chat_id, str(user_id_to_act) + " заяка на верификацию отклонена")
                return

    except ValueError:
        mes.text_message(chat_id, "Неверный формат id")
        return True
    return False


def set_code(user_id, code, chat_id):
    print(code)
    db.set_referral_code(code, user_id)
    mes.text_message(chat_id,
                     "Пользователю успешно присвоен реферальный код ")


#
def adding_new_user(user_id: str):
    db.add_user(user_id, int(time.time()))
    db.add_row_to_vtickets(user_id)


#
def auto_actions():
    while True:
        actions = db.get_available_auto_actions(time.time())
        # [0] action_type
        #   1 [1] post_id, counts, plus_time, rate_id, [5] message_id, maxcount

        for action in actions:
            if action[0] == 1:
                mes.send_post(ID_POST_CHANNEL, action[1])
                new_actions = action[2] + 1

                if action[6] > new_actions:
                    tt = int(time.time())
                    db.set_post_last_up_and_used_counts(action[1], tt, new_actions)
                    db.set_next_post_up_in_auto_post(action[1], new_actions,
                                                     tt + action[3])
                else:
                    db.delete_auto_action_with_post_id(action[1])
                    db.set_post_auto_ups_info(action[1], 0, 0)
                    return

            elif actions[0] == 2:
                tb.edit_message_reply_markup(chat_id=ID_POST_CHANNEL,
                                             message_id=action[5])
                db.delete_auto_action_with_message_id(action[5])
        time.sleep(120)


#
if __name__ == "__main__":
    Thread(target=auto_actions).start()

    tb.polling(none_stop=True)

