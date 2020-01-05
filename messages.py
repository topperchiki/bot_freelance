from telebot import types
import db
from bot import tb
from constants import *
import os
import time


# Building
def main_menu_building(user_id: str or int):
    count = db.get_user_posts_count(user_id)[0]

    text = "Главное меню"

    mark_up = types.InlineKeyboardMarkup(row_width=2)
    mark_up.add(types.InlineKeyboardButton('Мои объявления: ' + str(count),
                                           callback_data='postpage:1'),
                types.InlineKeyboardButton('Новое объявление',
                                           callback_data="sideMenu"))
    mark_up.add(types.InlineKeyboardButton('Платные услуги',
                                           callback_data="paidServices"),
                types.InlineKeyboardButton('Пригласить друга',
                                           callback_data="referral"))

    return text, mark_up


def side_menu_building():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    a = types.InlineKeyboardButton(text="Исполнитель", callback_data="createPost:fr")
    b = types.InlineKeyboardButton(text="Заказчик", callback_data="createPost:cu")
    c = types.InlineKeyboardButton(text="В главное меню", callback_data="mainMenu")
    keyboard.add(a, b, c)
    text = "Выберите тип"
    return text, keyboard


def paid_service_menu_building(user_id: str or int):
    text = 'Платные услуги'

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    a = types.InlineKeyboardButton(text="Реклама на канале", url=URL_CONTACT_ACC)
    if db.get_user_verification_status(user_id)[0]:
        b = types.InlineKeyboardButton(text="Верифицирован ✅", callback_data="verification_1")
    else:
        b = types.InlineKeyboardButton(text="Верификация аккаунта", callback_data="verification_1")

    c = types.InlineKeyboardButton(text="Назад", callback_data="mainMenu")
    keyboard.add(a, b, c)

    return text, keyboard


def gen_keyboard_listing(now: int, num_all_pages: int):
    data = []
    if num_all_pages >= 5:
        data = [[1, "1"], [0, ""], [0, ""], [0, ""],
                [num_all_pages, str(num_all_pages)]]
        if now == 1:
            data[0][1] = "•1•"
            data[1] = [2, "2"]
            data[2] = [3, "3"]
            data[3] = [4, "4"]
            data[4][1] = data[4][1] + "»"
        elif now == num_all_pages:
            data[4][1] = "•" + data[4][1] + "•"
            data[1] = [num_all_pages - 3, str(num_all_pages - 3)]
            data[2] = [num_all_pages - 2, str(num_all_pages - 2)]
            data[3] = [num_all_pages - 1, str(num_all_pages - 1)]
            data[0][1] = "«" + data[0][1]
        elif num_all_pages - 1 == now:
            data[3][1] = "•" + data[3][1] + "•"
            data[1] = [num_all_pages - 3, str(num_all_pages - 3)]
            data[2] = [num_all_pages - 2, str(num_all_pages - 2)]
            data[0][1] = "«" + data[0][1]
        elif now + 1 == 2:
            data[0][1] = "1"
            data[1] = [2, "•2•"]
            data[2] = [3, "3"]
            data[3] = [4, "4"]
            data[4][1] = data[4][1] + "»"
        else:
            data[1] = [now - 1, "‹" + str(now - 1)]
            data[2] = [now, "•" + str(now) + "•"]
            data[3] = [now + 1, str(now + 1) + "›"]
    elif num_all_pages != 1:
        for i in range(1, num_all_pages + 1):
            if i != now:
                data.append([i, str(i)])
            else:
                data.append([i, "•" + str(i) + "•"])
    return data


def nice_time(time_value: int):
    seconds = time_value % 60
    minutes = time_value % 3600 // 60
    hours = time_value % 86400 // 3600
    days = time_value // 86400

    text = ""
    if days:
        text += str(days) + " дн."
    if hours:
        if text:
            text += " " + str(hours) + " ч."
        else:
            text += str(hours) + " ч."
    if minutes:
        if text:
            text += " " + str(minutes) + " мин."
        else:
            text += str(minutes) + " мин."
    if seconds:
        if text:
            text += " " + str(seconds) + " сек."
        else:
            text += str(seconds) + " сек."
    return text


def get_posts_on_page(user_id: str or int, page: int):
    posts = db.get_user_posts(user_id, (page - 1) * 10, 10)
    if len(posts) == 0:
        if page == 1:
            text = "Нет опубликованных объявлений"
        else:
            text = "На этой странице нет объявлений"
        text += "\n\n----------\nОсталось ручных подъемов ☆ - " + str(
            db.get_user_manual_ups(user_id)[0])
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="mainmenu"))
        return text, keyboard

    # Кол-во возможных страниц
    all_pages = int(len(posts) / 10) + (1 if len(posts) % 10 else 0)
    if page > all_pages:
        page = 1

    # Начальная страница
    start = (page - 1) * 10
    # Добавление объявлений с данной страницы в сообщение
    text = ""

    for post_id in posts[start: start + 10]:
        post = db.get_post_info(post_id[0])
        # type, title, category, time_last_up, rate_id, auto_ups, auto_ups_used
        text += "/open_post_" + str(post_id[0]) + "\n"
        if post[0] == 1:
            text += "#Исполнитель\n"
        elif post[1] == 2:
            text += "#Заказчик+\n"
        ti = post[1]
        if len(ti) > 30:
            ti = ti[:27] + "..."
        text += "Название " + ti + "\n"
        text += "Категория: " + db.get_category_hashtag(post[2].split(";")[-1])[0] + "\n"
        text += time.strftime("Поднято: %H:%M:%S %d.%m.%Y", time.gmtime(post[3])) + "\n"
        has_up = False
        if post[4]:
            text += "АвтоПодъемы (кол-во/поднятие раз в): " + str(post[5] - post[6]) + "/" + nice_time(db.get_rate_time(post[4])[0])
            has_up = True
        if has_up:
            text += "\n\n"
        else:
            text += "АвтоПодъемы: ❌\n\n"

    text += "----------\nОсталось ручных подъемов ☆ - " + str(db.get_user_manual_ups(user_id)[0])
    data = gen_keyboard_listing(page, all_pages)
    keyboard = types.InlineKeyboardMarkup(row_width=len(data) + 1)
    buttons = []
    for i in data:
        buttons.append(types.InlineKeyboardButton(text=i[1], callback_data="postpage:" + str(i[0])))
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="mainmenu"))
    return text, keyboard


def generate_help(admin=False):
    return (T_HELP if not admin else T_HELP_ADMIN)


def edit_pbp_menu_building(post_type: int):
    text = "Изменить"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if post_type == 1:
        keyboard.add(types.InlineKeyboardButton(text="Категории",
                                                callback_data="edit_pbp_categories_fr_n_0"),
                     types.InlineKeyboardButton(text="Название",
                                                callback_data="edit_pbp_title_fr"))
        keyboard.add(types.InlineKeyboardButton(text="Описание",
                                                callback_data="edit_pbp_description_fr"),
                     types.InlineKeyboardButton(text="Памятку",
                                                callback_data="edit_pbp_memo"))
        keyboard.add(types.InlineKeyboardButton(text="Портфолио",
                                                callback_data="edit_pbp_portfolio_fr"),
                     types.InlineKeyboardButton(text="Контакты",
                                                callback_data="edit_pbp_contacts_fr"))
        keyboard.add(types.InlineKeyboardButton(text="Оплату",
                                                callback_data="edit_pbp_payment_fr"),
                     types.InlineKeyboardButton(text="Наличие гаранта",
                                                callback_data="edit_pbp_guarantee_fr"))
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="preview_post_fr_bm"))  # back menu
    elif post_type == 2:
        keyboard.add(types.InlineKeyboardButton(text="Категории",
                                                callback_data="edit_pbp_categories_cu_n_0"),
                     types.InlineKeyboardButton(text="Название",
                                                callback_data="edit_pbp_title_cu"))
        keyboard.add(types.InlineKeyboardButton(text="Описание",
                                                callback_data="edit_pbp_description_ cu"),
                     types.InlineKeyboardButton(text="Контакты",
                                                callback_data="edit_pbp_contacts_cu"))
        keyboard.add(types.InlineKeyboardButton(text="Необходимость портфолио",
                                                callback_data="edit_pbp_portfolio_cu"))
        keyboard.add(types.InlineKeyboardButton(text="Оплату",
                                                callback_data="edit_pbp_payment_cu"),
                     types.InlineKeyboardButton(text="Наличие гаранта",
                                                callback_data="edit_pbp_guarantee_cu"))
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="preview_post_cu"))  # back menu

    return text, keyboard


def edit_pbp_payment_menu_building(user_id: str or int, post_type=1):

    text = "Выберите пункт"
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if post_type == 1:

        keyboard.add(types.InlineKeyboardButton(text="Изменить тип цены",
                                                callback_data="edit_pbp_payment"
                                                              "_type_fr_m"))
        pay_info = db.get_prepare_payment_info(user_id)  # type, price
        price = pay_info[1]

        if pay_info[0] == 2:
            keyboard.add(
                types.InlineKeyboardButton(text="Изменить: " + str(price),
                                           callback_data="edit_pbp_price_fr"))
        elif pay_info[0] == 3:
            keyboard.add(types.InlineKeyboardButton(text="Изменить диапозон",
                                                    callback_data="edit_pbp_"
                                                                  "price_2_fr"))

        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="edit_pbp_"
                                                              "menu_fr"))

    else:

        keyboard.add(types.InlineKeyboardButton(text="Изменить тип цены",
                                                callback_data="edit_pbp_payment"
                                                              "_type_cu_m"))

        pay_info = db.get_prepare_payment_info(user_id)  # type, price
        price = pay_info[1]

        if pay_info[0] == 2:
            keyboard.add(
                types.InlineKeyboardButton(text="Изменить: " + str(price),
                                           callback_data="edit_pbp_price_cu"))
        elif pay_info[0] == 3:
            keyboard.add(types.InlineKeyboardButton(text="Изменить диапозон",
                                                    callback_data="edit_pbp_"
                                                                  "price_2_cu"))

        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="edit_pbp_"
                                                              "menu_cu"))
    return text, keyboard


def edit_pbp_payment_type_building(post_type=1):
    text = "Выберите тип цены"
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if post_type == 1:
        keyboard.add(types.InlineKeyboardButton(text="Договорная",
                                                callback_data="edit_pbp_payment_type_fr:1"))
        keyboard.add(types.InlineKeyboardButton(text="Фиксированная",
                                                callback_data="edit_pbp_payment_type_fr:2"))
        keyboard.add(types.InlineKeyboardButton(text="Диапозон цен",
                                                callback_data="edit_pbp_payment_type_fr:3"))
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="edit_pbp_payment_fr"))

    else:
        keyboard.add(types.InlineKeyboardButton(text="Договорная",
                                                callback_data="edit_pbp_payment_type_cu:1"))
        keyboard.add(types.InlineKeyboardButton(text="Фиксированная",
                                                callback_data="edit_pbp_payment_type_cu:2"))
        keyboard.add(types.InlineKeyboardButton(text="Диапозон цен",
                                                callback_data="edit_pbp_payment_type_cu:3"))
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="edit_pbp_payment_cu"))

    return text, keyboard


def get_post_building(post_id: str or int):
    post_id = str(post_id)

    post = db.get_post_all(post_id)
    text = ""
    # Разные части
    if post[0] == 1:  # Freelance
        text = "#Исполнитель\nНазвание: " + post[1] + "\n\nОписание: " + \
               post[2] + "\n"
        text += "Памятка: " + (post[3] if bool(post[3]) else "нет")

    elif post[0] == 2:  # Customer
        text = "#Заказчик\nНазвание: " + post[1] + "\n\nОписание: " + \
               post[2] + "\n"
        text += "Портфолио: " + (
            "необходимо" if bool(post[4]) else "необязательно")

    # Общая часть
    text += "\nКонтакты: " + post[5] + "\n\n"
    categories = [int(i) for i in post[6].split(";")]
    hashtags = db.get_hashtags_categories_with_ids(categories)
    d = dict()
    for i in hashtags:
        d[i[0]] = i[1]

    for cat in categories:
        text += d[cat] + " "
    text += "\n"
    if post[8] == 1:
        text += "Договорная"
    elif post[8] == 2:
        text += str(post[7]) + " $"
    elif post[8] == 3:
        a, b = post[7].split(";")
        text += "От " + a + " до " + b + " $"

    text += "\n"
    text += "Гарант: " + ("✅" if post[9] else "❌") + "\n\n"
    if post[0] == 2:
        text += "Портфолио: " + (
            "необходимо\n" if post[4] else "необязательно\n")
    text += "Опубликовано: " + time.strftime("%H:%M:%S %d.%m.%Y",
                                             time.gmtime(post[10])) + "\n"
    text += "Поднято последний раз: " + time.strftime("%H:%M:%S %d.%m.%Y",
                                                      time.gmtime(post[11]))

    text += "\n"
    if post[14]:
        rate_time = db.get_rate_time(post[14])[0]
        text += "Подъемы раз в " + nice_time(rate_time) + \
                "✅, осталось " + str(post[12] - post[13])
        text += "\n"
    else:
        text += "Нет автоматических подъемов\n"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if post[0] == 1 and len(post[4]) > 0:
        keyboard.add(
            types.InlineKeyboardButton(text="Портфолио", url=post[4]))
    keyboard.add(types.InlineKeyboardButton(text="Редактировать", callback_data="noanswer"))
                                            #callback_data="edit:" + post_id))
    manual_ups = db.get_user_manual_ups(post[15])
    if int(time.time()) - 10800 >= post[11]:
        keyboard.add(types.InlineKeyboardButton(text="Поднять (" + str(manual_ups[0]) + ")", callback_data="up_" + post_id))
    else:
        keyboard.add(types.InlineKeyboardButton(text="Поднято ✅ (" + str(
                                                manual_ups[0]) + ")", callback_data="up_" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Купить подъемы", callback_data="buying_Ups_Menu:" + post_id))
    return text, keyboard


def send_prepared_post_building(user_id: str or int,
                                only_post=False):
    post_info = db.get_prepared_post(user_id)
    text = ""

    if post_info[0] == 1:
        db.set_user_step(user_id, 15)
        text += "Исполнитель"

    else:
        db.set_user_step(user_id, 110)
        text += "Заказчик"

    text += "\nНазвание: " + post_info[1]
    text += "\nОписание: " + post_info[2]

    if post_info[0] == 1:
        text += "\nПортфолио: " + (post_info[5] if post_info[5] else "отсутствует")
    else:
        text += "\nПортфолио: " + (
            "необходимо" if post_info[5] else "не обязательно")

    text += "\nКонтакты: " + post_info[6]
    text += "\nРабота через гарант-бота: " + ("✅" if post_info[9] else "❌")

    if post_info[0] == 1:
        text += "\n" + post_info[4]

    if post_info[7] == 1:
        text += "\nЦена: договорная"
    elif post_info[7] == 2:
        text += "\nЦена: " + post_info[8] + " $"
    elif post_info[7] == 3:
        minimum_price, maximum_price = post_info[8].split(";")
        text += "\nЦена: " + minimum_price + " - " + maximum_price + " $"

    text += "\nКатегории: "
    categories = [int(i) for i in post_info[3].split(";")]
    categories_hashtags = db.get_hashtags_categories_with_ids(categories)
    d_cat = dict()
    for cat in categories_hashtags:
        d_cat[cat[0]] = cat[1]

    for category in categories:
        text += d_cat[category] + ", "

    text = text[:-2]

    if not only_post:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="Опубликовать",
                                                callback_data="post_" + ("fr" if post_info[0] == 1
                                                   else "cu")))
        keyboard.add(types.InlineKeyboardButton(text="Редактировать",
                                                callback_data=
                                                "edit_pbp_menu_"
                                                + ("fr" if post_info[0] == 1
                                                   else "cu")))
        return text, keyboard
    else:
        return text, False


def send_verification_ticket_building(user_id: str or int, page: int = 1):
    if page == 1:
        text, status = db.get_verification_ticket_text_and_status(user_id)
    else:
        text, status = db.get_verification_ticket_contacts_and_status(user_id)

    if (status >> 7 & 1):
        return verified_by_admin_building()

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    if not (status >> 4 & 1):

        if len(text) == 0:
            text = "Пусто"

        if page == 1:
            keyboard.add(types.InlineKeyboardButton(text="Редактировать",
                                                    callback_data="verification_edit_1"))
        else:
            keyboard.add(types.InlineKeyboardButton(text="Редактировать",
                                                    callback_data="verification_edit_2"))

        if page == 1:
            keyboard.add(types.InlineKeyboardButton(text="•Описание•",
                                                    callback_data="noanswer"),
                         types.InlineKeyboardButton(text="Контакты",
                                                    callback_data="verification_2"))
        elif page == 2:
            keyboard.add(types.InlineKeyboardButton(text="Описание",
                                                    callback_data="verification_1"),
                         types.InlineKeyboardButton(text="•Контакты•",
                                                    callback_data="noanswer"))

        if not (status >> 3 & 1):
            keyboard.add(types.InlineKeyboardButton(text="Оплатить (500 р.)",
                                                    callback_data="verification_pay"))
        else:
            keyboard.add(types.InlineKeyboardButton(text="Оплачено",
                                                    callback_data="noanswer"))

            filled = ((status >> 1) & 1) + ((status >> 2) & 1)
            if filled == 2:
                keyboard.add(types.InlineKeyboardButton(text="Отправить на рассмотрение",
                                                        callback_data="verification_send"))
            elif filled == 1:
                keyboard.add(
                    types.InlineKeyboardButton(text="Заявка заполнена (1/2)",
                                               callback_data="noanswer"))
            elif filled == 0:
                keyboard.add(
                    types.InlineKeyboardButton(text="Заявка заполнена (0/2)",
                                               callback_data="noanswer"))

    else:

        if page == 1:
            keyboard.add(types.InlineKeyboardButton(text="•Описание•",
                                                    callback_data="noanswer"),
                         types.InlineKeyboardButton(text="Контакты",
                                                    callback_data="verification_2"))
        elif page == 2:
            keyboard.add(types.InlineKeyboardButton(text="Описание",
                                                    callback_data="verification_1"),
                         types.InlineKeyboardButton(text="•Контакты•",
                                                    callback_data="noanswer"))

        keyboard.add(types.InlineKeyboardButton(text="Заявка отправлена", callback_data="noanswer"))
        if not (status >> 5 & 1):
            keyboard.add(
                types.InlineKeyboardButton(text="На рассмотрении ⌚",
                                           callback_data="noanswer"))
            keyboard.add(
                types.InlineKeyboardButton(text="Отменить отправку",
                                           callback_data="verification_cancel"))
        else:
            if (status >> 6) & 1:
                keyboard.add(
                    types.InlineKeyboardButton(text="Подтверждена ✅",
                                               callback_data="noanswer"))
            else:
                keyboard.add(
                    types.InlineKeyboardButton(text="Отказано ❌",
                                               callback_data="noanswer"))
                keyboard.add(
                    types.InlineKeyboardButton(text="Новая заявка",
                                               callback_data="verification_new_ticket"))

    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="paidservices"))
    return text, keyboard


def buying_ups_menu_building(post_id: str or int):
    post_id = str(post_id)
    text = "Выберите тип"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Ручные",
                                            callback_data="buying_ups_manual"))
    keyboard.add(types.InlineKeyboardButton(text="Автоматические",
                                            callback_data="buying_ups_auto_" + post_id))
    return text, keyboard


def verified_by_admin_building():
    text = "Вы верифицированы администратором"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="paidservices"))
    return text, keyboard


#
def main_menu_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 1)

    text, mark_up = main_menu_building(user_id)

    tb.send_message(chat_id=chat_id, text=text, reply_markup=mark_up)


def main_menu(chat_id: str or int, message_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 1)

    text, mark_up = main_menu_building(user_id)
    tb.edit_message_text(text, chat_id, message_id, reply_markup=mark_up)


def side_menu_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 2)

    text, kb = side_menu_building()
    tb.send_message(chat_id, text, reply_markup=kb)


def side_menu(chat_id: str or int, message_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 2)

    text, kb = side_menu_building()
    tb.edit_message_text(text, chat_id, message_id, reply_markup=kb)


def text_message(chat_id: str or int, text: str):
    tb.send_message(text=text, chat_id=chat_id)


def send_posts_page(chat_id: str or int, message_id: str or int, user_id: str or int, page: int):
    db.set_user_step(user_id, 1)
    text, keyboard = get_posts_on_page(user_id, page)
    if text is None:
        return
    tb.edit_message_text(text=text, message_id=message_id, chat_id=chat_id, reply_markup=keyboard)


def send_posts_page_nm(chat_id: str or int, user_id: str or int, page: int):
    db.set_user_step(user_id, 1)
    text, keyboard = get_posts_on_page(user_id, page)
    if text is None:
        return
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def post_doesnt_exist_message(chat_id: str or int):
    tb.send_message(text="Объявления с таким id не существует\nФормат запроса /id_postЧисло", chat_id=chat_id)


def failed_showing_post(chat_id: str or int):
    tb.send_message(text="Произошла ошибка", chat_id=chat_id)


def help_nm(chat_id: int or str, admin=False):
    text = generate_help(admin)
    tb.send_message(chat_id=chat_id, text=text)


def generate_referral(chat_id, user_id):
    code = '666'
    sms = URL_ACTION_START_REFERRAL + code

    tb.send_message(chat_id=chat_id, text = sms)


def paid_service_menu_nm(chat_id: int or str, user_id: int or str):
    db.set_user_step(user_id, 1)

    text, mark_up = paid_service_menu_building(user_id)

    tb.send_message(chat_id=chat_id, text=text, reply_markup=mark_up)


def paid_service_menu(chat_id: int or str,
                      message_id: str or int, user_id: int or str):
    db.set_user_step(user_id, 1)

    text, mark_up = paid_service_menu_building(user_id)

    tb.edit_message_text(chat_id=chat_id, message_id=message_id,
                         text=text, reply_markup=mark_up)


def categories_post(chat_id: str or int, message_id: str or int, user_id: str or int, post_type=1):
    customer = False
    if post_type == 2:
        customer = True

    if customer:
        db.set_user_step(user_id, 100)
    else:
        db.set_user_step(user_id, 4)

    categories = db.get_categories_ids_names_with_parent(0)
    text_pattern = "category_" + ("cu" if customer else "fr") + "_n_"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category[1],
                                                callback_data=text_pattern + str(category[0])))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="sideMenu"))
    text = "Выберите категорию"
    tb.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


def categories_post_nm(chat_id: str or int, user_id: str or int, post_type=1):
    customer = False
    if post_type == 2:
        customer = True

    if customer:
        db.set_user_step(user_id, 100)
    else:
        db.set_user_step(user_id, 4)

    categories = db.get_categories_ids_names_with_parent(0)
    text_pattern = "category_" + ("cu" if customer else "fr") + "_n_"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category[1],
                                                callback_data=text_pattern +
                                                              str(category[0])))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="sideMenu"))
    text = "Выберите категорию"
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def subcategories_post(chat_id: str or int, message_id: str or int, category_to_show: str or int, user_id: str or int, post_type=1):
    customer = False
    if post_type == 2:
        customer = True

    if customer:
        db.set_user_step(user_id, 100)
    else:
        db.set_user_step(user_id, 4)

    categories = db.get_categories_ids_names_with_parent(category_to_show)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    text_pattern = "category_" + ("cu" if customer else "fr")
    text_pattern2 = text_pattern + "_b_"
    text_pattern += "_n_"

    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category[1], callback_data=text_pattern + str(category[0])))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=text_pattern2 + str(db.get_category_parent(category_to_show)[0])))
    text = "Выберите категорию"
    tb.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


def subcategories_post_nm(chat_id: str or int, category_to_show: str or int, user_id: str or int, post_type=1):
    customer = False
    if post_type == 2:
        customer = True

    if customer:
        db.set_user_step(user_id, 100)
    else:
        db.set_user_step(user_id, 4)

    categories = db.get_categories_ids_names_with_parent(category_to_show)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    text_pattern = "category_" + ("cu" if customer else "fr")
    text_pattern2 = text_pattern + "_b_"
    text_pattern += "_n_"

    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category[1],
                                                callback_data=text_pattern +
                                                              str(category[0])))

    keyboard.add(types.InlineKeyboardButton("Назад",
                                            callback_data=text_pattern2 + str(db.get_category_parent(
                                                category_to_show))))
    text = "Выберите категорию"
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_title_freelance_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 5)
    text = "Название услуги (не более " +\
           str(FREELANCE_TITLE_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))

    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def set_description_freelance_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 6)

    text = "Описание услуги (не более " +\
           str(FREELANCE_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))

    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def set_memo_freelance_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 7)

    text = "Памятка заказчику (не более " +\
           str(FREELANCE_MEMO_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))

    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def set_portfolio_freelance_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 8)

    text = "Отправьте ссылку на портфолио, если есть"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Пропустить",
                                            callback_data="portfolio_fr_skip"))
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_contacts_freelance_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 9)

    text = "Контакты (не более " + \
           str(FREELANCE_CONTACTS_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))
    tb.send_message(chat_id= chat_id, text=text, reply_markup=keyboard)


def set_payment_type_freelance_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 10)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная",
                                            callback_data="payment_type_fr:1"))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная",
                                            callback_data="payment_type_fr:2"))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон цен",
                                            callback_data="payment_type_fr:3"))
    text = "Выберите тип цены"
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_fixed_price_freelance_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 11)

    tb.send_message(text="Введите цену в долларах, $", chat_id=chat_id)


def is_guarantee_necessary_freelance_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 14)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да",
                                            callback_data="guarantee_fr:1"),
                 types.InlineKeyboardButton(text="Нет",
                                            callback_data="guarantee_fr:0"))
    text = "Согласны проводить сделку через гарант-бота?"

    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_range_price_1_freelance_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 12)

    text = "Введите минимум, $"
    tb.send_message(text=text, chat_id=chat_id)


def set_range_price_2_freelance_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 13)

    text = "Введите максимум, $"
    tb.send_message(text=text, chat_id=chat_id)


def set_title_customer_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 101)
    text = "Название услуги (не более " + \
           str(CUSTOMER_TITLE_LETTERS_LIMIT) + " символов)"

    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))

    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def set_description_customer_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 102)

    text = "Описание услуги (не более " + str(CUSTOMER_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))

    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def set_portfolio_customer_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 103)

    text = "Нужно ли портфолио?"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да",
                                            callback_data="portfolio_cu:1"),
                 types.InlineKeyboardButton(text="Нет",
                                            callback_data="portfolio_cu:0"))

    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_contacts_customer_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 104)

    text = "Контакты (не более " + \
           str(CUSTOMER_CONTACTS_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="В главное меню"))

    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def set_payment_type_customer_post_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 105)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная",
                                            callback_data="payment_type_cu:1"))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная",
                                            callback_data="payment_type_cu:2"))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон цен",
                                            callback_data="payment_type_cu:3"))

    text = "Выберите тип цены"
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_fixed_price_customer_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 106)

    tb.send_message(text="Введите цену в долларах, $", chat_id=chat_id)


def is_guarantee_necessary_customer_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 109)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да",
                                            callback_data="guarantee_cu:1"),
                 types.InlineKeyboardButton(text="Нет",
                                            callback_data="guarantee_cu:0"))
    text = "Согласны проводить сделку через гарант-бота?"

    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def set_range_price_1_customer_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 107)

    text = "Введите минимум, $"
    tb.send_message(text=text, chat_id=chat_id)


def set_range_price_2_customer_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 108)

    text = "Введите максимум, $"
    tb.send_message(text=text, chat_id=chat_id)


def back_prepare_post_menu(chat_id: str or int, message_id: str or int,
                           user_id: str or int):
    post_type = db.get_prepare_post_type(user_id)[0]
    if post_type == 1:
        db.set_user_step(user_id, 15)
    else:
        db.set_user_step(user_id, 110)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Опубликовать",
                                            callback_data="post"))
    keyboard.add(types.InlineKeyboardButton(text="Редактировать",
                                            callback_data=
                                            "edit_pbp_menu_"
                                            + "fr" if post_type == 1
                                            else "cu"))
    tb.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


def edit_pbp_menu(chat_id: str or int, message_id: str or int,
                  user_id: str or int, post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 31)
    else:
        db.set_user_step(user_id, 124)

    text, keyboard = edit_pbp_menu_building(post_type)
    tb.edit_message_text(text=text, message_id=message_id, chat_id=chat_id,
                         reply_markup=keyboard)


def edit_pbp_menu_nm(chat_id: str or int, user_id: str or int, post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 31)
    else:
        db.set_user_step(user_id, 124)

    text, keyboard = edit_pbp_menu_building(post_type)
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def edit_pbp_title_nm(chat_id: str or int, user_id: str or int, post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 17)
        text = "Введите новое название " + "(не более " + str(
            FREELANCE_TITLE_LETTERS_LIMIT) + " символов)"
    else:
        db.set_user_step(user_id, 111)
        text = "Введите новое название " + "(не более " + str(
            CUSTOMER_TITLE_LETTERS_LIMIT) + " символов)"

    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_description_nm(chat_id: str or int, user_id: str or int,
                            post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 18)
        text = "Введите новое описание " + "(не более " + str(
            FREELANCE_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    else:
        db.set_user_step(user_id, 112)
        text = "Введите новое название " + "(не более " + str(
            CUSTOMER_DESCRIPTION_LETTERS_LIMIT) + " символов)"

    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_memo_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 19)

    text = "Введите новую памятку " + "(не более " + str(
        FREELANCE_MEMO_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_portfolio_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 20)

    text = "Оставьте ссылку на свое портфолио"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Удалить",
                                            callback_data="edit_pbp_portfolio_fr_n"))
    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def edit_pbp_portfolio(chat_id: str or int, message_id: str or int,
                       user_id: str or int):
    db.set_user_step(user_id, 113)

    text = "Нужно ли портфолио?"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да",
                                            callback_data="edit_pbp_portfolio_cu_1"),
                 types.InlineKeyboardButton(text="Нет",
                                            callback_data="edit_pbp_portfolio_cu_0"))
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="edit_pbp_menu_cu"))
    tb.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                         reply_markup=keyboard)


def edit_pbp_contacts_nm(chat_id: str or int, user_id: str or int, post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 21)

        text = "Введите новые контакты" + "(не более " + str(
            FREELANCE_CONTACTS_LETTERS_LIMIT) + " символов)"
        tb.send_message(chat_id=chat_id, text=text)

    else:
        db.set_user_step(user_id, 114)

        text = "Введите новые контакты" + "(не более " + str(
            CUSTOMER_CONTACTS_LETTERS_LIMIT) + " символов)"
        tb.send_message(chat_id=chat_id, text=text)

    return


def edit_pbp_categories(chat_id: str or int, message_id: str or int,
                        category_to_show: str or int, user_id: str or int,
                        post_type=1):
    customer = False
    if post_type == 2:
        customer = True

    if customer:
        db.set_user_step(user_id, 125)
    else:
        db.set_user_step(user_id, 32)

    categories = db.get_categories_ids_names_with_parent(category_to_show)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    text_pattern = "edit_pbp_categories_" + ("cu" if customer else "fr")
    text_pattern2 = text_pattern + "_b_"
    text_pattern += "_n_"

    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category[1],
                                                callback_data=text_pattern + str(
                                                    category[0])))

    if str(category_to_show) == "0":
        keyboard.add(types.InlineKeyboardButton("Назад",
                                                callback_data="edit_pbp_menu_" + ("fr" if not customer else "cu")))
    else:
        keyboard.add(types.InlineKeyboardButton("Назад", callback_data=text_pattern2))
    text = "Выберите категорию"
    tb.edit_message_text(text=text, chat_id=chat_id, message_id=message_id,
                         reply_markup=keyboard)


def edit_pbp_payment_menu(chat_id: str or int, message_id: str or int,
                          user_id: str or int, post_type=1):

    if post_type == 1:
        db.set_user_step(user_id, 22)
    else:
        db.set_user_step(user_id, 115)

    text, keyboard = edit_pbp_payment_menu_building(user_id, post_type)
    tb.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                         reply_markup=keyboard)


def edit_pbp_payment_menu_nm(chat_id: str or int, user_id: str or int, post_type=1):

    if post_type == 1:
        db.set_user_step(user_id, 22)
    else:
        db.set_user_step(user_id, 115)

    text, keyboard = edit_pbp_payment_menu_building(user_id, post_type)
    tb.send_message(chat_id=chat_id, text=text,
                         reply_markup=keyboard)


def edit_pbp_fixed_price_nm(chat_id: str or int, user_id: str or int,
                            post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 24)
    else:
        db.set_user_step(user_id, 117)

    text = "Введите цену, $"
    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_price_nm(chat_id: str or int, user_id: str or int, post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 27)
    else:
        db.set_user_step(user_id, 120)

    text = "Введите новое число, $"
    tb.send_message(text=text, chat_id=chat_id)


def edit_pbp_price_range_nm(chat_id: str or int, user_id: str or int,
                            post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 28)
    else:
        db.set_user_step(user_id, 121)

    text = "Введите минимум, $"
    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_price_range_2_nm(chat_id: str or int, user_id: str or int,
                              post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 29)
    else:
        db.set_user_step(user_id, 122)

    text = "Введите максимумальную цену, $"
    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_range_price_1_nm(chat_id: str or int, user_id: str or int,
                              post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 25)
    else:
        db.set_user_step(user_id, 118)

    text = "Введите минимуальную цену, $"
    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_range_price_2_nm(chat_id: str or int, user_id: str or int,
                              post_type=1):
    if post_type == 1:
        db.set_user_step(user_id, 26)
    else:
        db.set_user_step(user_id, 119)

    text = "Введите максимальную цену, $"
    tb.send_message(chat_id=chat_id, text=text)


def edit_pbp_guarantee(chat_id: str or int, message_id: str or int, user_id: str or int, post_type=1):
    text = "Работа через гарант-бота?"
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if post_type == 1:
        db.set_user_step(user_id, 25)

        keyboard.add(types.InlineKeyboardButton(text="Да",
                                                callback_data="edit_pbp_guarantee_fr_y"))
        keyboard.add(types.InlineKeyboardButton(text="Нет",
                                                callback_data="edit_pbp_guarantee_fr_n"))
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="edit_pbp_menu_fr"))
    else:
        db.set_user_step(user_id, 118)

        keyboard.add(types.InlineKeyboardButton(text="Да",
                                                callback_data="edit_pbp_guarantee_cu_y"))
        keyboard.add(types.InlineKeyboardButton(text="Нет",
                                                callback_data="edit_pbp_guarantee_cu_n"))
        keyboard.add(types.InlineKeyboardButton(text="Назад",
                                                callback_data="edit_pbp_menu_cu"))

    tb.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)


def edit_pbp_payment_type(chat_id: str or int, message_id: str or int,
                          user_id: str or int, post_type=1):

    text, keyboard = edit_pbp_payment_type_building(post_type)

    if post_type == 1:
        db.set_user_step(user_id, 23)

    else:
        db.set_user_step(user_id, 116)

    tb.edit_message_text(text=text, message_id=message_id, chat_id=chat_id,
                         reply_markup=keyboard)


def edit_pbp_payment_type_nm(chat_id: str or int, user_id: str or int, post_type=1):
    text, keyboard = edit_pbp_payment_type_building(post_type)

    if post_type == 1:
        db.set_user_step(user_id, 23)

    else:
        db.set_user_step(user_id, 116)

    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def send_post(chat_id: str or int, post_id: str or int):
    post = db.get_post(post_id)

    text = ""
    if post[0] == 1:
        text += "#Исполнитель"
    else:
        text += "#Заказчик"

    text += "\n\n"
    text += "<b>Название:</b> " + post[1] + "\n"
    text += "<b>Описание:</b> " + post[2] + "\n"
    if post[0] == 1:
        text += ("<b>Памятка заказчику:</b> " + post[3] +
                 "\n" if len(post[3]) > 0 else "")
    else:
        text += ("<b>Портфолио:</b> необходимо\n" if bool(
            post[4]) else "<b>Портфолио:</b> необязательно\n")
    text += "<b>Контакты:</b> " + post[5] + "\n"
    text += "<b>Гарант:</b> " + ("✅" if post[8] else "❌") + "\n\n"
    if post[6] == 1:
        text += "<b>Договорная</b>, "
    elif post[6] == 2:
        text += "<b>" + str(post[7]) + " $</b>, "
    elif post[6] == 3:
        a, b = post[7].split(";")
        text += "<b>" + str(a) + " - " + str(b) + " $</b>, "
    categories = [int(i) for i in post[9].split(";")]
    hashtags = db.get_hashtags_categories_with_ids(categories)
    d = dict()
    for i in hashtags:
        d[i[0]] = i[1]

    for cat in categories:
        text += d[cat] + ", "

    text = text[:-2] + "\n"
    text += "\n===============\nПодать объявление можно с помощью бота @" + BOT_USERNAME
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if bool(post[4]) and post[0] == 1:
        keyboard.add(types.InlineKeyboardButton(text="Портфолио",
                                                url=post[4]))

    keyboard.add(types.InlineKeyboardButton(text="Пожаловаться",
                                            callback_data="report:" + str(post_id)))
    return tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard,
                           parse_mode="html")


def posted(chat_id: str or int, user_id: str or int, post_id: str or int):
    db.set_user_step(user_id, 69)

    post_id = str(post_id)
    text = "Успешно опубликовано\nID вашего объявления " + post_id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Купить подъемы",
                                            callback_data="buying_Ups_Menu:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="В главное меню",
                                            callback_data="mainMenu"))
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def get_post(chat_id: str or int, message_id: str or int, post_id: str or int):
    text, keyboard = get_post_building(post_id)

    tb.edit_message_text(text=text, chat_id=chat_id, message_id=message_id,
                         reply_markup=keyboard)


def get_post_nm(chat_id: str or int, post_id: str or int):
    text, keyboard = get_post_building(post_id)

    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def send_prepared_post_nm(chat_id: str or int, user_id: str or int,
                                only_post=False):
    text, keyboard = send_prepared_post_building(user_id, only_post)

    if only_post:
        tb.send_message(chat_id=chat_id, text=text)

    else:
        tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def send_prepared_post(chat_id: str or int, message_id: str or int,
                       user_id: str or int, only_post=False):
    text, keyboard = send_prepared_post_building(user_id, only_post)

    if only_post:
        tb.edit_message_text(chat_id=chat_id, text=text, message_id=message_id)

    else:
        tb.edit_message_text(chat_id=chat_id, text=text, message_id=message_id,
                             reply_markup=keyboard)


def send_verification_ticket(chat_id: str or int, message_id: str or int,
                             user_id: str or int, page=1):

    db.set_user_step(user_id, 2)
    text, keyboard = send_verification_ticket_building(user_id, page)
    tb.edit_message_text(text=text, message_id=message_id,
                         chat_id=chat_id, reply_markup=keyboard)


def send_verification_ticket_nm(chat_id: str or int, user_id: str or int, page=1):

    db.set_user_step(user_id, 2)
    text, keyboard = send_verification_ticket_building(user_id, page)
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def enter_verification_text_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 151)
    text = "Ввведите текст"
    tb.send_message(chat_id=chat_id, text=text)


def enter_verification_contacts_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 152)
    text = "Ввведите контакты"
    tb.send_message(chat_id=chat_id, text=text)


def send_approve_verification_ticket_nm(chat_id: str or int, user_id: str or int):
    user_id = str(user_id)

    text_t, contacts = db.get_verification_ticket_text_and_contacts(user_id)
    text = "Заявка от пользователя " + user_id + "\n\n" + text_t + "\n\n" + contacts
    text += "\n--------------\n/approve_v_" + user_id + "\n" + "/deny_v_" + user_id

    tb.send_message(chat_id=chat_id, text=text)


def pay_verification(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 153)

    f = [types.LabeledPrice(label='Verification', amount=500 * 100)]
    tb.send_invoice(chat_id, 'Подтверждение аккаунта', 'Верификация',
                    '201', PAYMENT_PROVIDER, 'RUB', f, start_parameter='f')


def buying_ups_menu(chat_id: str or int, message_id: str or int,
                    user_id: str or int, post_id: str or int):
    db.set_user_step(user_id, 160)
    text, keyboard = buying_ups_menu_building(post_id)
    tb.edit_message_text(chat_id=chat_id, message_id=message_id,
                         reply_markup=keyboard, text=text)


def buying_ups_menu_nm(chat_id: str or int, user_id: str or int, post_id: str or int):
    db.set_user_step(user_id, 160)
    text, keyboard = buying_ups_menu_building(post_id)
    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def enter_manual_ups_nm(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 161)
    text = "Введите количество подъемов (от 1 до 100)"
    tb.send_message(chat_id=chat_id, text=text)


def available_auto_rates(chat_id: str or int, message_id: str or int,
                         user_id: str or int, post_id: str or int):
    db.set_user_step(user_id, 162)
    rates = db.get_showed_rates()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if not len(rates):
        text = "К сожалению, сейчас нет доступных вариантов автоматических подъемов"
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="buying_ups_menu_" + str(post_id)))
        tb.edit_message_text(text=text, chat_id=chat_id,
                             message_id=message_id, reply_markup=keyboard)
        return
    text = "Выберите тариф"
    post_id = str(post_id)
    for rate in rates:
        t = "1 раз в " + nice_time(rate[1]) + " (" + str(rate[2]) + "р.)"
        cl_data = "buying_ups_rate_" + str(post_id) + "_" + str(rate[0])
        keyboard.add(types.InlineKeyboardButton(text=t, callback_data=cl_data))

    tb.edit_message_text(text=text, reply_markup=keyboard,
                         message_id=message_id, chat_id=chat_id)


def enter_auto_ups(chat_id: str or int, user_id: str or int):
    db.set_user_step(user_id, 163)

    text = "Введите количество подъемов (от 1 до 100)"
    tb.send_message(chat_id=chat_id, text=text)


def send_invoice_manual_ups(chat_id: str or int, user_id: str or int,
                            manual_ups: int):
    manual_ups_str = str(manual_ups)
    f = [types.LabeledPrice(label='Ручные поднятия ' + manual_ups_str,
                            amount=MANUAL_UPS_PRICE * int(manual_ups) * 100)]
    tb.send_invoice(chat_id, 'Покупка подъемов', 'Ручные поднятия ' + manual_ups_str,
                        '202_' + manual_ups_str, PAYMENT_PROVIDER, 'RUB', f, start_parameter='f')


def verification_paid(chat_id: str or int):
    text = "Заявка на верификацию оплачена"
    tb.send_message(chat_id=chat_id, text=text)


def verified_by_admin(chat_id: str or int, message_id: str or int):
    text, keyboard = verified_by_admin_building()
    tb.edit_message_text(text=text, chat_id=chat_id,
                         message_id=message_id, reply_markup=keyboard)


def post_has_auto_ups(chat_id: str or int, message_id: str or int,
                      post_id: str or int):
    post_id = str(post_id)
    text = "Дождитесь, пока у данного объявления " \
           "не закончатся предыдущие автоматические подъемы"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Назад",
                                   callback_data="get_" + str(post_id)))
    tb.edit_message_text(text=text, chat_id=chat_id,
                         message_id=message_id, reply_markup=keyboard)


def send_auto_ups_invoice(chat_id: str or int,
                          user_id: str or int, post_id: str or int,
                          rate_id: str or int, price: int, ups: int):
    ups_str = str(ups)
    f = [types.LabeledPrice(label='Автоматические поднятия ' + ups_str,
                            amount=100 * int(ups) * price)]
    tb.send_invoice(chat_id, 'Покупка подъемов',
                    'Автоматические поднятия ' + ups_str,
                    '203_' + str(rate_id) + ":" +
                    str(post_id) + "=" + ups_str,
                    PAYMENT_PROVIDER, 'RUB', f, start_parameter='f')


def no_manual_ups_nm(chat_id: str or int, post_id: str or int):
    post_id = str(post_id)
    text = "У вас нет ручных подъемов"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Купить", callback_data="buying_ups_menu_" + post_id))
    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


# TODO  reports messages
# def send_report_ticket(chat_id: str or int, post_id: str or int):
#     post_id = str(post_id)
#
#     text = "Жалоба на пост"