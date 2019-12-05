from telebot import types
import db
from bot import tb
from constants import *
import os
import time


# Building
def main_menu_building(user_id: str or int):
    count = db.get_count_user_posts(user_id)

    text = "Главное меню"

    mark_up = types.InlineKeyboardMarkup(row_width=2)
    mark_up.add(types.InlineKeyboardButton('Мои объявления: ' + str(count), callback_data='postpage:1'),
                types.InlineKeyboardButton('Новое объявление', callback_data="sideMenu"))
    mark_up.add(types.InlineKeyboardButton('Платные услуги', callback_data="paidServices"),
                types.InlineKeyboardButton('Пригласить друга', callback_data="referal"))

    return text, mark_up


def generate_referal(user_id,chat_id):
    code = 'https://t.me/Mytoserbot?start='.join([hex(ord(c)).replace('0x','') for c in os.urandom(8)])
    sms = 'Пригласите 5 друзей по данной ссылке и получите 1 ручной подъем! ' + code
    tb.send_message(chat_id, 'Пригласите 5 друзей по данной ссылке и получите 1 ручной подъем! ')


def side_menu_building():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    a = types.InlineKeyboardButton(text="Исполнитель", callback_data="createPost:fr")
    b = types.InlineKeyboardButton(text="Заказчик", callback_data="createPost:cu")
    c = types.InlineKeyboardButton(text="В главное меню", callback_data="mainMenu")
    keyboard.add(a, b, c)
    text = "Выберите тип"
    return text, keyboard


def take_text_mes(message):
    text = message.text
    return text


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
    if len(posts) == 0:
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
