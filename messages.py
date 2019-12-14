from telebot import types
import db
from bot import tb
from constants import *
import os
import time


# Building
def main_menu_building(user_id: str or int,value):
    count = len(db.get_count_user_posts(user_id))

    text = "Главное меню"

    mark_up = types.InlineKeyboardMarkup(row_width=2)
    mark_up.add(types.InlineKeyboardButton('Мои объявления: ' + str(count), callback_data='postpage:1'),
                types.InlineKeyboardButton('Новое объявление', callback_data="sideMenu"))
    mark_up.add(types.InlineKeyboardButton('Платные услуги', callback_data="paidServices"),
                types.InlineKeyboardButton('Пригласить друга', callback_data="referral"))
    if value == True:
        mark_up.add(types.InlineKeyboardButton('Администрация', callback_data="admin_panel"))

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
    b = None
    if db.get_user_verification_status(user_id):
        b = types.InlineKeyboardButton(text="Верифицирован ✅", callback_data="noanswer")
    else:
        b = types.InlineKeyboardButton(text="Верификация аккаунта", callback_data="verification")
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
    minutes = time_value % 3600
    hours = time_value % 216000
    days = time_value % 12960000

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
    return text


def get_posts_on_page(chat_id: str or int, user_id: str or int, page: int):
    posts = db.get_user_posts(user_id)

    if len(posts[0]) == 0:
        text = "Нет опубликованных объявлений"
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
        post = db.get_post_info(post_id)
        # type, title, category, time_last_up, rate_id, auto_ups
        text += "/id_post" + str(post_id) + "\n"
        if post[0] == 1:
            text += "#Исполнитель\n"
        elif post[1] == 2:
            text += "#Заказчик+\n"
        ti = post[1]
        if len(ti) > 30:
            ti = ti[:27] + "..."
        text += "Наименование" + ti + "\n"
        text += "Категория: " + db.get_category_hashtag([post[2].split(";")[-1]]) + "\n"
        text += time.strftime("Поднято: %H:%M:%S %d.%m.%Y", time.gmtime(post[3])) + "\n"
        has_up = False
        if post[4]:
            text += "АвтоПодъемы (кол-во/ поднятие раз в): " + str(post[5]) + "/" + nice_time(db.get_rate_time(post[4]))
            has_ups = True
        if has_ups:
            text += "\n\n"
        else:
            text += "АвтоПодъемы: ❌\n\n"

    text += "----------\nОсталось ручных апов ☆ - " + str(db.get_user_manual_ups(user_id))

    data = gen_keyboard_listing(page, all_pages)
    keyboard = types.InlineKeyboardMarkup(row_width=len(data) + 1)
    buttons = []
    for i in data:
        buttons.append(types.InlineKeyboardButton(text=i[1], callback_data="postpage:" + str(i[0])))
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="mainmenu"))
    return text, keyboard


def generate_help():
    return T_HELP


#
def main_menu_nm(chat_id: str or int, user_id: str or int, value: bool):
    db.set_user_step(user_id, 1)

    text, mark_up = main_menu_building(user_id, value)

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
    text, keyboard = get_posts_on_page(chat_id, user_id, page)
    if text is None:
        return
    tb.edit_message_text(text=text, message_id=message_id, chat_id=chat_id, reply_markup=keyboard)


def send_posts_page_nm(chat_id: str or int, user_id: str or int, page: int):
    text, keyboard = get_posts_on_page(chat_id, user_id, page)
    if text is None:
        return
    tb.send_message(text=text, chat_id=chat_id, reply_markup=keyboard)


def post_doesnt_exist_message(chat_id: str or int):
    tb.send_message(text="Объявления с таким id не существует\nФормат запроса /id_postЧисло", chat_id=chat_id)


def failed_showing_post(chat_id: str or int):
    tb.send_message(text="Произошла ошибка", chat_id=chat_id)


def help_nm(chat_id: int or str):
    text = generate_help()
    tb.send_message(chat_id=chat_id, text=text)


def generate_referral(chat_id, user_id):
    code = '666'
    sms = 'Пригласите 5 друзей по данной ссылке и получите 1 ручной подъем! '+ 'https://t.me/Mytoserbot?start=' + code

    tb.send_message(chat_id=chat_id, text = sms)


def paid_service_menu_nm(chat_id: int or str, user_id: int or str):
    db.set_user_step(user_id, 1)

    text, mark_up = paid_service_menu_building(user_id)

    tb.send_message(chat_id=chat_id, text=text, reply_markup=mark_up)


def paid_service_menu(chat_id: int or str, message_id: str or int, user_id: int or str):
    db.set_user_step(user_id, 1)

    text, mark_up = paid_service_menu_building(user_id)

    tb.send_message(chat_id=chat_id, message_id=message_id, text=text, reply_markup=mark_up)


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
                                                              category[0]))

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
        keyboard.add(types.InlineKeyboardButton(text=category[1], callback_data=text_pattern + category[0]))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=text_pattern2 + db.get_category_parent(category_to_show)))
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


