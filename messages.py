from telebot import types
from bot import tb
from constants import *
import work_with_files as wwf
import time
from telebot.types import LabeledPrice


# Разные меню


# Создание текста и клавиатуры главного меню
def main_menu_building(message: types.Message):
    # Получаем ID объявлений, которыми владеет пользователь
    posts_table = wwf.load_table(P_OWNERSHIPS).get(str(message.chat.id), [])

    mark_up = types.InlineKeyboardMarkup(row_width=2)
    mark_up.add(types.InlineKeyboardButton('Мои объявления: ' + str(len(posts_table)), callback_data="1001"), types.InlineKeyboardButton('Новое объявление', callback_data="sideMenu"))
    mark_up.add(types.InlineKeyboardButton('Платные услуги', callback_data="paidServices"))
    text = "Главное меню"
    return text, mark_up


# Отправка главного меню в новом сообщении
def main_menu_nm(message: types.Message):  # Main Menu in new message
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 1
    wwf.save_table(users_table, P_USERS)

    text, mark_up = main_menu_building(message)

    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=mark_up)


# Отправка главного меню через редактирование

def main_menu(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 1
    wwf.save_table(users_table, P_USERS)

    text, mark_up = main_menu_building(message)
    tb.edit_message_text(text, message.chat.id, message.message_id, reply_markup=mark_up)


# Меню Заказчик/Исполнитель для нового объявления
def side_menu_building(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    a = types.InlineKeyboardButton(text="Исполнитель", callback_data="createFreelancerPost")
    b = types.InlineKeyboardButton(text="Заказчик", callback_data="createCustomerPost")
    c = types.InlineKeyboardButton(text="В главное меню", callback_data="mainMenu")
    keyboard.add(a, b, c)
    text = "Выберите тип"
    return text, keyboard


def side_menu_nm(message: types.Message):  # Side Menu in new message
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 2
    wwf.save_table(users_table, P_USERS)

    text, kb = side_menu_building(message)
    tb.send_message(message.chat.id, text, reply_markup=kb)


def side_menu(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 2
    wwf.save_table(users_table, P_USERS)

    text, kb = side_menu_building(message)
    tb.edit_message_text(text, message.chat.id, message.message_id, reply_markup=kb)


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


def get_posts_on_page(message: types.Message, page: int, manual_ups: int):
    ownership_table = wwf.load_table(P_OWNERSHIPS)
    posts = ownership_table.get(str(message.chat.id), [])
    if len(posts) == 0:
        text = "У вас нет опубликованных объявлений"
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="В главное меню",
                                                callback_data="mainMenu"))
        tb.edit_message_text(text, message.chat.id, message.message_id, reply_markup=keyboard)
        return None, None

    # Кол-во возможных страниц
    all_pages = int(len(posts) / 10) + (1 if len(posts) % 10 else 0)
    if page > all_pages:
        page = 1

    # Начальная страница
    start = (page - 1) * 10
    # Добавление объявлений с данной страницы в сообщение
    text = ""
    posts_info = wwf.load_table(P_POSTS)
    for i in posts[start: start + 10]:
        post = posts_info[str(i)]
        text += "/id_post" + str(post["post_id"]) + "\n"
        if post["type"] == 1:
            text += "#Исполнитель\n"
        else:
            text += "#Заказчик+\n"
        ti = post["title"]
        if len(ti) > 30:
            ti = ti[:27] + "..."
        text += "Наименование" + ti + "\n"
        cat_table = wwf.load_table(P_CATEGORIES)
        text += "Категория: " + cat_table[post["categories"][-1]]["hashtag"] + "\n"
        text += time.strftime("Поднято: %H:%M:%S %d.%m.%Y", time.gmtime(post["time_upped"])) + "\n"
        has_ups = False
        if post["auto_ups"]:
            if post["auto_ups_type"] == 1:
                text += "АвтоПодъемы: ★ " + str(post["auto_ups"])
                has_ups = True
            elif post["auto_ups_type"] == 2:
                text += "АвтоПодъемы: ★★ " + str(post["auto_ups"])
                has_ups = True
            elif post["auto_ups_type"] == 3:
                text += "АвтоПодъемы: ★★★ " + str(post["auto_ups"])
                has_ups = True
        if has_ups:
            text += "\n"
        if not has_ups:
            text += "АвтоПодъемы: ❌\n"
        text += "\n"

    text += "----------\nПодсказка АвтоПодъемы:\nПодъемы:\n★ - 1 раз в 24 часа\n★★ - 1 раз в 12 часов\n★★★ - 1 раз в 6 часов\n\nОсталось ручных апов ☆ - " + str(manual_ups)

    data = gen_keyboard_listing(page, all_pages)
    keyboard = types.InlineKeyboardMarkup(row_width=len(data) + 1)
    buttons = []
    for i in data:
        buttons.append(types.InlineKeyboardButton(text=i[1], callback_data=str(1000 + i[0])))
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="mainMenu"))
    return text, keyboard


def send_posts_page(message: types.Message, page: int):
    users_table = wwf.load_table(P_USERS)
    text, keyboard = get_posts_on_page(message, page, users_table[str(message.chat.id)]["manual_ups"])
    if text is None:
        return
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def post_doesnt_exist_message(message: types.Message):
    tb.send_message(text="Объявления с таким id не существует\nФормат запроса /id_postЧисло", chat_id=message.chat.id)


def post_access_denied(message: types.Message):
    tb.send_message(text="Доступ запрещен", chat_id=message.chat.id)


def send_post_building(message: types.Message, post_id: str or int, manual_ups: int):
    posts_table = wwf.load_table(P_POSTS)
    post_id = str(post_id)
    if not str(post_id) in posts_table:
        post_doesnt_exist_message(message)
        return None, None

    if posts_table[post_id]["owner_id"] != str(message.chat.id):
        post_access_denied(message)
        return None, None

    post = posts_table[post_id]
    text = ""
	# Разные части
    if post["type"] == 1:  # Freelance
        text = "#Исполнитель\nНазвание: " + post["title"] + "\n\nОписание: " + post["description"] + "\n"
        text += "Памятка: " + (post["memo"] if bool(post["memo"]) else "нет")

    elif post["type"] == 2:  # Customer
        text = "#Заказчик\nНазвание: " + post["title"] + "\n\nОписание: " + post["description"] + "\n"
        text += "Портфолио: " + ("необходимо" if bool(post["portfolio"]) else "необязательно")

    # Общая часть
    text += "\nКонтакты: " + post["contacts"] + "\n\n"
    categories = wwf.load_table(P_CATEGORIES)
    for cat in post["categories"]:
        text += categories[cat]["hashtag"] + " "
    text += "\n"
    if post["payment_type"] == 1:
        text += "Договорная"
    elif post["payment_type"] == 2:
        text += str(post["price"]) + " $"
    elif post["payment_type"] == 3:
        text += "От " + str(post["price"][0]) + " до " + str(post["price"][1]) + " $"
    text += "\n"
    text += "Гарант: " + ("✅" if post["guarantee"] else "❌") + "\n\n"
    if post["type"] == 2:
        text += "Портфолио: " + ("необходимо\n" if post["portfolio"] else "необязательно\n")
    text += "Опубликовано: " + time.strftime("%H:%M:%S %d.%m.%Y",
                                             time.gmtime(post["time_published"])) + "\n"
    text += "Поднято последний раз: " + time.strftime("%H:%M:%S %d.%m.%Y", time.gmtime(post["time_upped"]))

    text += "\n"
    has_ups = False
    if post["auto_ups"]:
        if post["auto_ups_type"] == 1:
            text += "Подъемы 1/24 ✅, осталось " + str(post["auto_ups"])
            has_ups = True
        elif post["auto_ups_type"] == 2:
            text += "Подъемы 1/12 ✅, осталось " + str(post["auto_ups"])
            has_ups = True
        elif post["auto_ups_type"] == 3:
            text += "Подъемы 1/6 ✅, осталось " + str(post["auto_ups"])
            has_ups = True
    if has_ups:
        text += "\n"
    if not has_ups:
        text += "Нет подъемов\n"

    index = list(posts_table.keys()).index(post_id) + 1
    ownership_table = wwf.load_table(P_OWNERSHIPS)
    posts = ownership_table.get(post_id, [])
    page_code = str(index // 10 + (1 if bool(index % 10) else 0) + 1000)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if post["type"] == 1 and len(post["portfolio"]) > 0:
        keyboard.add(types.InlineKeyboardButton(text="Портфолио", url=post["portfolio"]))
    keyboard.add(types.InlineKeyboardButton(text="Редактировать", callback_data="edit:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Поднять (" + str(manual_ups) + ")", callback_data="up:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Купить подъемы", callback_data="buyingUpsMenu:" + post_id))
    return text, keyboard


def send_post(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 1
    wwf.save_table(users_table, P_USERS)

    text, keyboard = send_post_building(message, post_id, users_table[post_id["owner"]]["manual_ups"])
    if text is None:
        return
    tb.edit_message_text(text=text, reply_markup=keyboard, chat_id=message.chat.id, message_id=message.message_id)


def send_post_nm(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 1
    wwf.save_table(users_table, P_USERS)

    text, keyboard = send_post_building(message, post_id, users_table[post_id["owner"]]["manual_ups"])
    if text is None:
        return
    tb.send_message(text=text, reply_markup=keyboard, chat_id=message.chat.id)


def categories_post(message, customer=False):
    users_table = wwf.load_table(P_USERS)
    if customer:
        users_table[str(message.chat.id)]["condition"] = 100
    else:
        users_table[str(message.chat.id)]["condition"] = 4
    wwf.save_table(users_table, P_USERS)

    categories_r_table = wwf.load_table(P_CATEGORIES_R)
    categories_info_table = wwf.load_table(P_CATEGORIES)
    category_rprofile = categories_r_table["1"]
    text_pattern = "category_" + ("cu:" if customer else "fr:")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in category_rprofile["children"]:
        keyboard.add(types.InlineKeyboardButton(text=categories_info_table[category]["name"],
                                                callback_data=text_pattern + category))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="sideMenu"))
    text = "Выберите категорию"
    tb.edit_message_text(text=text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)


def categories_post_nm(message, customer=False):  # Categories Menu in new message
    users_table = wwf.load_table(P_USERS)
    if customer:
        users_table[str(message.chat.id)]["condition"] = 100
    else:
        users_table[str(message.chat.id)]["condition"] = 4
    wwf.save_table(users_table, P_USERS)

    categories_r_table = wwf.load_table(P_CATEGORIES_R)
    categories_info_table = wwf.load_table(P_CATEGORIES)
    category_rprofile = categories_r_table["1"]
    text_pattern = "category_" + ("cu:" if customer else "fr:")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in category_rprofile["children"]:
        keyboard.add(types.InlineKeyboardButton(text=categories_info_table[category]["name"],
                                                callback_data=text_pattern + category))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="sideMenu"))
    text = "Выберите категорию"
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def subcategories_post(message, parent_category, customer=False):
    users_table = wwf.load_table(P_USERS)
    if customer:
        users_table[str(message.chat.id)]["condition"] = 100
    else:
        users_table[str(message.chat.id)]["condition"] = 4
    wwf.save_table(users_table, P_USERS)

    categories_r_table = wwf.load_table(P_CATEGORIES_R)
    categories_info_table = wwf.load_table(P_CATEGORIES)
    category_rprofile = categories_r_table[parent_category]  # Category Relationship Profile
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    text_pattern = "category_" + ("cu:" if customer else "fr:")
    text_pattern2 = "category_back_" + ("cu:" if customer else "fr:")
    for category in category_rprofile["children"]:
        keyboard.add(types.InlineKeyboardButton(text=categories_info_table[category]["name"],
                                                callback_data=text_pattern + category))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=text_pattern2 + category_rprofile["parent"]))
    text = "Выберите категорию"
    tb.edit_message_text(text=text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)


def subcategories_post_nm(message, parent_category, customer=False):
    users_table = wwf.load_table(P_USERS)
    if customer:
        users_table[str(message.chat.id)]["condition"] = 100
    else:
        users_table[str(message.chat.id)]["condition"] = 4
    wwf.save_table(users_table, P_USERS)

    categories_r_table = wwf.load_table(P_CATEGORIES_R)
    categories_info_table = wwf.load_table(P_CATEGORIES)
    category_rprofile = categories_r_table[parent_category]  # Category Relationship Profile
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    text_pattern = "category_" + ("cu:" if customer else "fr:")
    text_pattern2 = "category_back_" + ("cu:" if customer else "fr:")
    for category in category_rprofile["children"]:
        keyboard.add(types.InlineKeyboardButton(text=categories_info_table[category]["name"],
                                                callback_data=text_pattern + category))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=text_pattern2 + category_rprofile["parent"]))
    text = "Выберите категорию"
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_title_freelance_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 5
    wwf.save_table(users_table, P_USERS)

    text = "Название услуги (не более " + str(FREELANCE_TITLE_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_description_freelance_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 6
    wwf.save_table(users_table, P_USERS)

    text = "Описание услуги (не более " + str(FREELANCE_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_memo_freelance_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 7
    wwf.save_table(users_table, P_USERS)

    text = "Памятка заказчику (не более " + str(FREELANCE_MEMO_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_portfolio_freelance_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 8
    wwf.save_table(users_table, P_USERS)

    text = "Отправьте ссылку на портфолио, если есть"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="no_portfolio_fr"))
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_contacts_freelance_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 9
    wwf.save_table(users_table, P_USERS)

    text = "Контакты (не более " + str(FREELANCE_CONTACTS_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_payment_type_freelance_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 10
    wwf.save_table(users_table, P_USERS)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная", callback_data="payment_type_fr:1"))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная", callback_data="payment_type_fr:2"))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон цен", callback_data="payment_type_fr:3"))
    text = "Выберите тип цены"
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_fixed_price_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 11
    wwf.save_table(users_table, P_USERS)

    tb.send_message(text="Введите цену в долларах, $", chat_id=message.chat.id)


def is_guarantee_necessary_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 14
    wwf.save_table(users_table, P_USERS)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="guarantee_fr:1"), types.InlineKeyboardButton(text="Нет", callback_data="guarantee_fr:0"))
    text = "Согласны проводить сделку через гарант-бота?"
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_range_price_1_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 12
    wwf.save_table(users_table, P_USERS)

    text = "Введите минимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def set_range_price_2_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 13
    wwf.save_table(users_table, P_USERS)

    text = "Введите максимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_pbp_menu_freelance_building(message: types.Message):  # post before posting - pbp
    text = "Изменить"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Категории", callback_data="edit_pbp_categories_fr:1"), types.InlineKeyboardButton(text="Название", callback_data="edit_pbp_title_fr"))
    keyboard.add(types.InlineKeyboardButton(text="Описание", callback_data="edit_pbp_description_fr"), types.InlineKeyboardButton(text="Памятку", callback_data="edit_pbp_memo_fr"))
    keyboard.add(types.InlineKeyboardButton(text="Портфолио", callback_data="edit_pbp_portfolio_fr"), types.InlineKeyboardButton(text="Контакты", callback_data="edit_pbp_contacts_fr"))
    keyboard.add(types.InlineKeyboardButton(text="Оплату", callback_data="edit_pbp_payment_fr"), types.InlineKeyboardButton(text="Наличие гаранта", callback_data="edit_pbp_guarantee_fr"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="preview_post_fr"))
    return text, keyboard


def edit_pbp_menu_freelance(message: types.Message):  # post before posting - pbp
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 31
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_menu_freelance_building(message)
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def edit_pbp_menu_freelance_nm(message: types.Message):  # post before posting - pbp
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 31
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_menu_freelance_building(message)
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def preview_post_mini(message: types.Message, customer=False):
    users_table = wwf.load_table(P_USERS)
    if customer:
        users_table[str(message.chat.id)]["condition"] = 110
    else:
        users_table[str(message.chat.id)]["condition"] = 15
    wwf.save_table(users_table, P_USERS)

    add_text = "fr"
    if customer:
        add_text = "cu"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Опубликовать",
                                            callback_data="post_" + add_text))
    keyboard.add(types.InlineKeyboardButton(text="Редактировать",
                                            callback_data="edit_pbp_menu_" + add_text))
    tb.edit_message_text(text="Выберите действие", chat_id=message.chat.id, message_id=message.message_id,
                         reply_markup=keyboard)


def edit_pbp_categories(message: types.Message, cat: str or int, customer=False):
    users_table = wwf.load_table(P_USERS)
    if customer:
        users_table[str(message.chat.id)]["condition"] = 125
    else:
        users_table[str(message.chat.id)]["condition"] = 32
    wwf.save_table(users_table, P_USERS)

    categories_info = wwf.load_table(P_CATEGORIES)
    ownership = wwf.load_table(P_CATEGORIES_R)
    atext = ("cu" if customer else "fr")
    text = "Выберите категорию"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category_id in ownership[cat]["children"]:
        keyboard.add(types.InlineKeyboardButton(text=categories_info[category_id]["name"],
                                                callback_data="edit_pbp_categories_" + atext + ":" + category_id))
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="edit_pbp_categories_b_" + atext + ":" + ownership[cat][
                                                "parent"]))
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def edit_pbp_title_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 17
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое название " + "(не более " + str(FREELANCE_TITLE_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_description_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 18
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое описание " + "(не более " + str(FREELANCE_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_memo_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 19
    wwf.save_table(users_table, P_USERS)

    text = "Введите новую памятку " + "(не более " + str(FREELANCE_MEMO_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_portfolio_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 20
    wwf.save_table(users_table, P_USERS)

    text = "Оставьте ссылку на свое портфолио"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Удалить", callback_data="edit_pbp_no_portfolio_fr"))
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_contacts_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 21
    wwf.save_table(users_table, P_USERS)

    text = "Введите новые контакты" + "(не более " + str(FREELANCE_CONTACTS_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_payment_freelance_building(message: types.Message):
    users_table = wwf.load_table(P_USERS)

    text = "Выберите пункт"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Изменить тип цены", callback_data="edit_pbp_payment_type_fr"))
    pay_type = users_table[str(message.chat.id)]["freelance_post"]["payment_type"]
    price = users_table[str(message.chat.id)]["freelance_post"]["price"]
    if pay_type == 2:
        keyboard.add(types.InlineKeyboardButton(text="Изменить: " + str(price), callback_data="edit_pbp_price_fr"))
    elif pay_type == 3:
        keyboard.add(types.InlineKeyboardButton(text="Изменить диапозон", callback_data="edit_pbp_price_2_fr"))

    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit_pbp_menu_fr"))
    return text, keyboard


def edit_pbp_payment_freelance(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 22
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_freelance_building(message)
    tb.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=keyboard)


def edit_pbp_payment_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 22
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_freelance_building(message)
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_payment_type_freelance_building(message: types.Message):
    text = "Выберите тип"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная",
                                            callback_data="edit_pbp_payment_type_2_fr:1"))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная",
                                            callback_data="edit_pbp_payment_type_2_fr:2"))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон",
                                            callback_data="edit_pbp_payment_type_2_fr:3"))
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="edit_pbp_payment_fr"))
    return text, keyboard


def edit_pbp_payment_type_freelance(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 23
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_type_freelance_building(message)
    tb.edit_message_text(message_id=message.message_id, chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_payment_type_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 23
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_type_freelance_building(message)
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_nt_fixed_price_freelance_nm(message: types.Message):  # nt - new type
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 24
    wwf.save_table(users_table, P_USERS)

    text = "Введите цену, $"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_nt_1_price_freelance_nm(message: types.Message):  # nt - new type
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 25
    wwf.save_table(users_table, P_USERS)

    text = "Введите минимуальную цену, $"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_nt_2_price_freelance_nm(message: types.Message):  # nt - new type
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 26
    wwf.save_table(users_table, P_USERS)

    text = "Введите максимальную цену, $"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_guarantee_freelance(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 30
    wwf.save_table(users_table, P_USERS)

    text = "Сделка через гарант-бота"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="edit_pbp_guarantee_yes_fr"), types.InlineKeyboardButton(text="Нет", callback_data="edit_pbp_guarantee_no_fr"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit_pbp_menu_fr"))
    tb.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=keyboard)


def edit_pbp_fixed_price_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 27
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое число, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_pbp_price_1_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 28
    wwf.save_table(users_table, P_USERS)

    text = "Введите минимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_pbp_price_2_freelance_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 29
    wwf.save_table(users_table, P_USERS)

    text = "Введите максимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def preview_post_freelance_nm(message: types.Message, post_struct, only_post=False):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 15
    wwf.save_table(users_table, P_USERS)

    blocks = []
    blocks.append("Исполнитель")
    blocks.append("Название: " + post_struct["title"])
    blocks.append("Описание: " + post_struct["description"])
    blocks.append("Памятка заказчику: " + post_struct["memo"])
    if bool(post_struct.get("portfolio", False)):
        blocks.append("Мое портфолио: " + post_struct["portfolio"])
    blocks.append("Контакты: " + post_struct["contacts"])
    blocks.append("Работа через гарант-бота: " + ("✅" if post_struct.get("guarantee", False) else "❌"))
    if post_struct["payment_type"] == 1:
        blocks.append("Цена: договорная")
    elif post_struct["payment_type"] == 2:
        blocks.append("Цена: " + str(post_struct["price"]) + " $")
    elif post_struct["payment_type"] == 3:
        blocks.append("Цена: " + str(post_struct["price"][0]) + " - " + str(
            post_struct["price"][1]) + " $")
    categories_info_table = wwf.load_table(P_CATEGORIES)
    cat_block = "Категории: "
    for cat in post_struct["categories"]:
        if len(categories_info_table[cat]["hashtag"]) + len(cat_block) > 1000:
            blocks.append(cat_block[:-2])
            cat_block = ""
        cat_block += categories_info_table[cat]["hashtag"] + ", "

    if len(cat_block) > 0:
        blocks.append(cat_block[:-2])

    blocks_buffer = []
    len_buffer = 0

    for block in blocks:
        if len(block) + len_buffer > 1000:
            tb.send_message(text='\n'.join(blocks_buffer), chat_id=message.chat.id)
            blocks_buffer = []
            len_buffer = 0
        blocks_buffer.append(block)
        len_buffer += len(block)

    if len(blocks_buffer) > 0:
        tb.send_message(text='\n'.join(blocks_buffer), chat_id=message.chat.id)

    if not only_post:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="Опубликовать", callback_data="post_fr"))
        keyboard.add(types.InlineKeyboardButton(text="Редактировать", callback_data="edit_pbp_menu_fr"))
        tb.send_message(text="Выберите действие", chat_id=message.chat.id, reply_markup=keyboard)


def post_nm(chat_id, post_struct):
    text = ""
    if post_struct["type"] == 1:
        text += "#Исполнитель"
    elif post_struct["type"] == 2:
        text += "#Заказчик"
    text += "\n\n"
    text += "<b>Название:</b> " + post_struct["title"] + "\n"
    text += "<b>Описание:</b> " + post_struct["description"] + "\n"
    if post_struct["type"] == 1:
        text += ("<b>Памятка заказчику:</b> " + post_struct["memo"] + "\n" if len(post_struct["memo"]) > 0 else "")
    else:
        text += ("<b>Портфолио:</b> необходимо\n" if bool(post_struct["portfolio"]) else "<b>Портфолио:</b> необязательно\n")
    text += "<b>Контакты:</b> " + post_struct["contacts"] + "\n"
    text += "<b>Гарант:</b> " + ("✅" if post_struct["guarantee"] else "❌") + "\n\n"
    if post_struct["payment_type"] == 1:
        text += "<b>Договорная</b>, "
    elif post_struct["payment_type"] == 2:
        text += "<b>" + str(post_struct["price"]) + " $</b>, "
    elif post_struct["payment_type"] == 3:
        text += "<b>" + str(post_struct["price"][0]) + " - " + str(post_struct["price"][1]) + " $</b>, "
    categories_info = wwf.load_table(P_CATEGORIES)
    for cat in post_struct["categories"]:
        text += categories_info[cat]["hashtag"] + ", "
    text = text[:-2] + "\n"
    text += "\n===============\nПодать объявление можно с помощью бота @" + BOT_USERNAME
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if bool(post_struct.get("portfolio", False)) and post_struct["type"] == 1:
        keyboard.add(types.InlineKeyboardButton(text="Портфолио", url=post_struct["portfolio"]))

    keyboard.add(types.InlineKeyboardButton(text="Пожаловаться", callback_data="report:" + post_struct["post_id"]))
    return tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="html")


def posted(message: types.Message, post_id):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 69
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text = "Успешно опубликовано\nID вашего объявления " + post_id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Купить подъемы", callback_data="buyingUpsMenu:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="mainMenu"))
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def error_message(message: types.Message, text: str):
    tb.send_message(text=text, chat_id=message.chat.id)


def rate(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    a = types.InlineKeyboardButton(text="1 раз в 24 часа",
                                   callback_data="coef1")
    b = types.InlineKeyboardButton(text="1 раз в 12 часов",
                                   callback_data="coef2")
    c = types.InlineKeyboardButton(text="1 раз в 6 часов",
                                   callback_data="coef3")
    d = types.InlineKeyboardButton(text="Вернуться", callback_data="аа")
    keyboard.add(a, b, c, d)
    tb.send_message(message.chat.id, 'Выберите для начала частоту автоподъёмника:', reply_markup=keyboard)


def paid_service_menu_building(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    text = 'Платные услуги'
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    a = types.InlineKeyboardButton(text="Реклама на канале", url=URL_CONTACT_ACC)
    b = None
    if users_table[str(message.chat.id)]["verified"]:
        b = types.InlineKeyboardButton(text="Верифицирован ✅", callback_data="noanswer")
    else:
        b = types.InlineKeyboardButton(text="Верификация аккаунта", callback_data="verification")
    c = types.InlineKeyboardButton(text="Назад", callback_data="mainMenu")
    keyboard.add(a, b, c)

    return text, keyboard


def paid_service_menu(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 3
    wwf.save_table(users_table, P_USERS)

    text, keyboard = paid_service_menu_building(message)
    tb.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text,
                         reply_markup=keyboard)


def paid_service_menu_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 3
    wwf.save_table(users_table, P_USERS)

    text, keyboard = paid_service_menu_building(message)
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def buying_ups_menu_building(message: types.Message, post_id: int or str):
    post_id = str(post_id)
    text = "Покупка подъемов для объявления " + post_id + "\nВыберите тип подъемов"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Автоматические", callback_data="buyingAutoUps:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Ручные", callback_data="buyingManualUps:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="К объявлению", callback_data="getPost:" + post_id))

    return text, keyboard


def buying_ups_menu(message: types.Message, post_id: int or str):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 70
    wwf.save_table(users_table, P_USERS)

    text, keyboard = buying_ups_menu_building(message, post_id)
    tb.edit_message_text(text=text, reply_markup=keyboard, message_id=message.message_id, chat_id=message.chat.id)


def buying_ups_menu_nm(message: types.Message, post_id: int or str):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 70
    wwf.save_table(users_table, P_USERS)

    text, keyboard = buying_ups_menu_building(message, post_id)
    tb.send_message(text=text, reply_markup=keyboard, chat_id=message.chat.id)


def buying_auto_ups_menu(message: types.Message, post_id: int or str):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 71
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text = "Выберите частоту подъемов по указанной стоимости для объявления ID:" + post_id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="1 раз в 24 часа - 10 руб.", callback_data="buyingAutoUpsMode:1:" + post_id))
    keyboard.add(
        types.InlineKeyboardButton(text="1 раз в 12 часов - 20 руб.", callback_data="buyingAutoUpsMode:2:" + post_id))
    keyboard.add(
        types.InlineKeyboardButton(text="1 раз в 6 часов - 30 руб.", callback_data="buyingAutoUpsMode:3:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="buyingUpsMenu:" + post_id))

    tb.edit_message_text(text=text, reply_markup=keyboard, message_id=message.message_id, chat_id=message.chat.id)


def buying_manual_ups_menu_nm(message: types.Message, post_id: int or str):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 72
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text = "Введите количество подъёмов для объявления (ID:" + post_id + ") от 1 до 100 (1 подъем = 10 руб.). Можно использовать не раньше, чем через 3 часа после последнего подъема"
    tb.send_message(text=text, chat_id=message.chat.id)


def enter_auto_ups_count_buying_nm(message: types.Message, post_id: int or str):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 73
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text = "Введите количество подъёмов от 1 до 100."
    tb.send_message(text=text, chat_id=message.chat.id)


def bill(message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 74
    wwf.save_table(users_table, P_USERS)

    pt = PAYMENT_PROVIDER
    orders_table = wwf.load_table(P_ORDERS)
    orders_table[str(message.chat.id)]["number"] = int(message.text)
    sms = 'Вы выбрали '
    sms += str(message.text)
    j = 'Oплата для ' + str(orders_table[str(message.chat.id)]["post_id"]) + " обьявления"
    g = str(int(message.text)) + 'UP'
    f = orders_table[str(message.chat.id)]["post_id"]
    if orders_table[str(message.chat.id)]["type"] == 'ap':
        if orders_table[str(message.chat.id)]["mode"] == 3:
            hours = str(24 // (int(orders_table[str(message.chat.id)]["mode"]) + 1))
        else:
            hours = str(24 // int(orders_table[str(message.chat.id)]["mode"]))
        sms += ' автоподьёмa(ов) с частотой 1 раз в ' + hours + ' часов. Цена ' + str(
            int(orders_table[str(message.chat.id)]["mode"]) * int(message.text) * 10) + "руб"
        tb.send_message(message.chat.id, sms)
        f = [LabeledPrice(label=g, amount=int(orders_table[str(message.chat.id)]["mode"]) * int(
            message.text) * 1000)]
        tb.send_invoice(message.chat.id, j, 'Автоподьёмы', '127', pt, 'RUB', f, start_parameter='d')
    else:
        sms += ' ручных подьёмов. Цена ' + str(int(message.text) * 10) + "руб"
        tb.send_message(message.chat.id, sms)
        f = [LabeledPrice(label='АП', amount=int(message.text) * 1000)]
        tb.send_invoice(message.chat.id, j, 'Ручные подьёмы', '127', pt, 'RUB', f, start_parameter='d')
    wwf.save_table(orders_table,P_ORDERS)


def buy_verification(message):
    pt = PAYMENT_PROVIDER
    f = [LabeledPrice(label='Verification', amount=500* 100)]
    tb.send_invoice(message.chat.id, 'Подтверждение аккаунта', 'Верификация', '126', pt, 'RUB', f, start_parameter='f')


def set_title_customer_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 101
    wwf.save_table(users_table, P_USERS)

    text = "Название услуги (не более " + str(CUSTOMER_TITLE_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_description_customer_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 102
    wwf.save_table(users_table, P_USERS)

    text = "Описание услуги (не более " + str(CUSTOMER_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_portfolio_customer_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 103
    wwf.save_table(users_table, P_USERS)

    text = "Нужно ли портфолио?"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="portfolio_cu:1"), types.InlineKeyboardButton(text="Нет", callback_data="portfolio_cu:0"))
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_contacts_customer_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 104
    wwf.save_table(users_table, P_USERS)

    text = "Контакты (не более " + str(CUSTOMER_CONTACTS_LETTERS_LIMIT) + " символов)"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"), types.KeyboardButton(text="В главное меню"))
    tb.send_message(message.chat.id, text, reply_markup=keyboard)


def set_payment_type_customer_post_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 105
    wwf.save_table(users_table, P_USERS)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная", callback_data="payment_type_cu:1"))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная", callback_data="payment_type_cu:2"))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон цен", callback_data="payment_type_cu:3"))
    text = "Выберите тип цены"
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_fixed_price_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 106
    wwf.save_table(users_table, P_USERS)

    tb.send_message(text="Введите цену в долларах, $", chat_id=message.chat.id)


def is_guarantee_necessary_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 109
    wwf.save_table(users_table, P_USERS)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="guarantee_cu:1"), types.InlineKeyboardButton(text="Нет", callback_data="guarantee_cu:0"))
    text = "Согласны проводить сделку через гарант-бота?"
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def set_range_price_1_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 107
    wwf.save_table(users_table, P_USERS)

    text = "Введите минимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def set_range_price_2_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 108
    wwf.save_table(users_table, P_USERS)

    text = "Введите максимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def preview_post_customer_nm(message: types.Message, post_struct, only_post=False):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 110
    wwf.save_table(users_table, P_USERS)

    blocks = []
    blocks.append("Заказчик")
    blocks.append("Название: " + post_struct["title"])
    blocks.append("Описание: " + post_struct["description"])
    blocks.append("Портфолио: " + ("необходимо" if post_struct.get("portfolio", False) else "не обязательно"))
    blocks.append("Контакты: " + post_struct["contacts"])
    blocks.append("Работа через гарант-бота: " + ("✅" if post_struct.get("guarantee", False) else "❌"))
    if post_struct["payment_type"] == 1:
        blocks.append("Цена: договорная")
    elif post_struct["payment_type"] == 2:
        blocks.append("Цена: " + str(post_struct["price"]) + " $")
    elif post_struct["payment_type"] == 3:
        blocks.append("Цена: " + str(post_struct["price"][0]) + " - " + str(
            post_struct["price"][1]) + " $")
    categories_info_table = wwf.load_table(P_CATEGORIES)
    cat_block = "Категории: "
    for cat in post_struct["categories"]:
        if len(categories_info_table[cat]["hashtag"]) + len(cat_block) > 1000:
            blocks.append(cat_block[:-2])
            cat_block = ""
        cat_block += categories_info_table[cat]["hashtag"] + ", "

    if len(cat_block) > 0:
        blocks.append(cat_block[:-2])

    blocks_buffer = []
    len_buffer = 0

    for block in blocks:
        if len(block) + len_buffer > 1000:
            tb.send_message(text='\n'.join(blocks_buffer), chat_id=message.chat.id)
            blocks_buffer = []
            len_buffer = 0
        blocks_buffer.append(block)
        len_buffer += len(block)

    if len(blocks_buffer) > 0:
        tb.send_message(text='\n'.join(blocks_buffer), chat_id=message.chat.id)

    if not only_post:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="Опубликовать", callback_data="post_cu"))
        keyboard.add(types.InlineKeyboardButton(text="Редактировать", callback_data="edit_pbp_menu_cu"))
        tb.send_message(text="Выберите действие", chat_id=message.chat.id, reply_markup=keyboard)


def edit_pbp_menu_customer_building(message: types.Message):  # post before posting - pbp
    text = "Изменить"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Категории", callback_data="edit_pbp_categories_cu:1"), types.InlineKeyboardButton(text="Название", callback_data="edit_pbp_title_cu"))
    keyboard.add(types.InlineKeyboardButton(text="Описание", callback_data="edit_pbp_description_cu"), types.InlineKeyboardButton(text="Контакты", callback_data="edit_pbp_contacts_cu"))
    keyboard.add(types.InlineKeyboardButton(text="Необходимость портфолио", callback_data="edit_pbp_portfolio_cu"))
    keyboard.add(types.InlineKeyboardButton(text="Оплату", callback_data="edit_pbp_payment_cu"), types.InlineKeyboardButton(text="Наличие гаранта", callback_data="edit_pbp_guarantee_cu"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="preview_post_cu"))
    return text, keyboard


def edit_pbp_menu_customer(message: types.Message):  # post before posting - pbp
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 124
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_menu_customer_building(message)
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def edit_pbp_menu_customer_nm(message: types.Message):  # post before posting - pbp
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 124
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_menu_customer_building(message)
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def edit_pbp_title_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 111
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое название " + "(не более " + str(CUSTOMER_TITLE_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_description_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 112
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое описание " + "(не более " + str(CUSTOMER_DESCRIPTION_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_portfolio_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 113
    wwf.save_table(users_table, P_USERS)

    text = "Нужно ли портфолио"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="edit_pbp_portfolio_1_cu:1"), types.InlineKeyboardButton(text="Нет", callback_data="edit_pbp_portfolio_1_cu:0"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit_pbp_menu_cu"))
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_contacts_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 114
    wwf.save_table(users_table, P_USERS)

    text = "Введите новые контакты" + "(не более " + str(CUSTOMER_CONTACTS_LETTERS_LIMIT) + " символов)"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_payment_customer_building(message: types.Message):
    users_table = wwf.load_table(P_USERS)

    text = "Выберите пункт"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Изменить тип цены", callback_data="edit_pbp_payment_type_cu"))
    pay_type = users_table[str(message.chat.id)]["customer_post"]["payment_type"]
    price = users_table[str(message.chat.id)]["customer_post"]["price"]
    if pay_type == 2:
        keyboard.add(types.InlineKeyboardButton(text="Изменить: " + str(price), callback_data="edit_pbp_price_cu"))
    elif pay_type == 3:
        keyboard.add(types.InlineKeyboardButton(text="Изменить диапозон", callback_data="edit_pbp_price_2_cu"))

    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit_pbp_menu_cu"))
    return text, keyboard


def edit_pbp_payment_customer(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 115
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_customer_building(message)
    tb.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=keyboard)


def edit_pbp_payment_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 115
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_customer_building(message)
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_payment_type_customer_building(message: types.Message):
    text = "Выберите тип"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная",
                                            callback_data="edit_pbp_payment_type_2_cu:1"))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная",
                                            callback_data="edit_pbp_payment_type_2_cu:2"))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон",
                                            callback_data="edit_pbp_payment_type_2_cu:3"))
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="edit_pbp_payment_cu"))
    return text, keyboard


def edit_pbp_payment_type_customer(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 116
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_type_customer_building(message)
    tb.edit_message_text(message_id=message.message_id, chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_payment_type_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 116
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_pbp_payment_type_customer_building(message)
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def edit_pbp_nt_fixed_price_customer_nm(message: types.Message):  # nt - new type
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 117
    wwf.save_table(users_table, P_USERS)

    text = "Введите цену, $"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_nt_1_price_customer_nm(message: types.Message):  # nt - new type
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 118
    wwf.save_table(users_table, P_USERS)

    text = "Введите минимуальную цену, $"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_nt_2_price_customer_nm(message: types.Message):  # nt - new type
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 119
    wwf.save_table(users_table, P_USERS)

    text = "Введите максимальную цену, $"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_pbp_guarantee_customer(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 123
    wwf.save_table(users_table, P_USERS)

    text = "Сделка через гарант-бота"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="edit_pbp_guarantee_yes_cu"), types.InlineKeyboardButton(text="Нет", callback_data="edit_pbp_guarantee_no_cu"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit_pbp_menu_cu"))
    tb.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=keyboard)


def edit_pbp_fixed_price_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 120
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое число, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_pbp_price_1_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 121
    wwf.save_table(users_table, P_USERS)

    text = "Введите минимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_pbp_price_2_customer_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 122
    wwf.save_table(users_table, P_USERS)

    text = "Введите максимум, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_post_menu_building(message: types.Message, post_id: str or int):
    post_id = str(post_id)
    posts_table = wwf.load_table(P_POSTS)
    p_type = posts_table[post_id]["type"]
    text = "Изменить"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Категории", callback_data="edit_categories:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Название", callback_data="edit_title:" + post_id), types.InlineKeyboardButton(text="Описание", callback_data="edit_description:" + post_id))
    if p_type == 1:
        keyboard.add(types.InlineKeyboardButton(text="Памятку", callback_data="edit_memo:" + post_id), types.InlineKeyboardButton(text="Портфолио", callback_data="edit_portfolio:" + post_id))
    elif p_type == 2:
        keyboard.add(
            types.InlineKeyboardButton(text="Необходимость портфолио", callback_data="edit_portfolio:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Контакты", callback_data="edit_contacts:" + post_id), types.InlineKeyboardButton(text="Оплату", callback_data="edit_payment:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Наличие гаранта", callback_data="edit_guarantee:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="getPost:" + post_id))
    return text, keyboard


def edit_post_menu(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 80
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_post_menu_building(message, post_id)
    tb.edit_message_text(text=text, reply_markup=keyboard, chat_id=message.chat.id, message_id=message.message_id)


def edit_post_menu_nm(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 80
    wwf.save_table(users_table, P_USERS)

    text, keyboard = edit_post_menu_building(message, post_id)
    tb.send_message(text=text, reply_markup=keyboard, chat_id=message.chat.id)


def edit_title_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 82
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое название"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_description_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 83
    wwf.save_table(users_table, P_USERS)

    text = "Введите новое описание"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_memo_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 84
    wwf.save_table(users_table, P_USERS)

    text = "Введите новую памятку"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_contacts_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 85
    wwf.save_table(users_table, P_USERS)

    text = "Введите новые контакты"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_portfolio_fr_nm(message: types.Message, post_id: int or str):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 86
    wwf.save_table(users_table, P_USERS)

    posts_table = wwf.load_table(P_POSTS)

    post_id = str(post_id)
    text = "Введите ссылку на портфолио"
    if len(posts_table[post_id]["portfolio"]) == 0:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="Удалить", callback_data="edit_portfolio_delete:" + post_id))
        tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)
    else:
        tb.send_message(text=text, chat_id=message.chat.id)


def edit_portfolio_cu(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 87
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text = "Нужно ли портфолио"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="edit_portfolio_yes:" + post_id), types.InlineKeyboardButton(text="Нет", callback_data="edit_portfolio_no:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit:" + post_id))
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def edit_guarantee(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 88
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text = "Нужна ли гарантия"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="edit_guarantee_yes:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data="edit_guarantee_no:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit:" + post_id))
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def edit_pay_building(meesage: types.Message, post_id: str or int):
    text = "Выберите тип цены"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Договорная", callback_data="edit_pay_type1:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Фиксированная", callback_data="edit_pay_type2:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Диапозон", callback_data="edit_pay_type3:" + post_id))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="edit:" + post_id))
    return text, keyboard


def edit_pay(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 89
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text, keyboard = edit_pay_building(message, post_id)
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def edit_pay_nm(message: types.Message, post_id: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 89
    wwf.save_table(users_table, P_USERS)

    post_id = str(post_id)
    text, keyboard = edit_pay_building(message, post_id)
    tb.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboard)


def edit_fixed_price_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 90
    wwf.save_table(users_table, P_USERS)
    text = "Введите цену, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_price_1_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 91
    wwf.save_table(users_table, P_USERS)
    text = "Введите минимальную цену, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_price_2_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 92
    wwf.save_table(users_table, P_USERS)
    text = "Введите максимальную цену, $"
    tb.send_message(text=text, chat_id=message.chat.id)


def edit_categories(message: types.Message, cat: str or int):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 81
    wwf.save_table(users_table, P_USERS)

    categories_info = wwf.load_table(P_CATEGORIES)
    ownership = wwf.load_table(P_CATEGORIES_R)
    text = "Выберите категорию"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category_id in ownership[cat]["children"]:
        keyboard.add(types.InlineKeyboardButton(text=categories_info[category_id]["name"],
                                                callback_data="edit_categories_1:" + category_id))
    keyboard.add(
        types.InlineKeyboardButton(text="Назад", callback_data="edit_categories_b:" + ownership[cat]["parent"]))
    tb.edit_message_text(text=text, message_id=message.message_id, chat_id=message.chat.id, reply_markup=keyboard)


def write_about_yourself_ver_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 75
    wwf.save_table(users_table, P_USERS)

    text = "Напишите кратко о себе и о своём опыте работы"
    tb.send_message(chat_id=message.chat.id, text=text)


def send_links_ver_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 76
    wwf.save_table(users_table, P_USERS)

    text = "На каких фриланс биржах вы зарегистрированы? Отправьте ссылки на профили"
    tb.send_message(chat_id=message.chat.id, text=text)


def preview_verification_request_nm(message: types.Message, user_struct):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 77
    wwf.save_table(users_table, P_USERS)

    ownerships_table = wwf.load_table(P_OWNERSHIPS)
    text = "Ваша заявка на верификацию:\n\n" + user_struct["verification_request"]["about"] + "\n" + user_struct["verification_request"]["links"] + "\nУ вас объявлений: " + str(len(ownerships_table[user_struct["user_id"]]))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Подтвердить", callback_data="payverification"))
    tb.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


def confirm_verification_nm(chat_id: str or int, user_struct):
    ownerships_table = wwf.load_table(P_OWNERSHIPS)
    text = "Заявка от пользователя ID:" + str(user_struct["user_id"]) + "\nНужно рассмотреть до " + time.strftime("%H:%M:%S %d.%m.%Y", time.gmtime(user_struct["verification_request_was_sent"] + 172800)) + "\n\n" + user_struct["verification_request"]["about"] + "\n" + user_struct["verification_request"]["links"] + "\nОбъявлений: " + str(len(ownerships_table[user_struct["user_id"]]))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Подтвердить", callback_data="verify:" + user_struct["user_id"]))
    keyboard.add(types.InlineKeyboardButton(text="Отказать", callback_data="unverify:" + user_struct["user_id"]))
    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def paid_verification_nm(message: types.Message):
    users_table = wwf.load_table(P_USERS)
    users_table[str(message.chat.id)]["condition"] = 78
    wwf.save_table(users_table, P_USERS)

    text = "Ваша заявка отправлена на рассмотрение"
    tb.send_message(chat_id=message.chat.id, text=text)


def edit_verification_status(message: types.Message, user_id: str or int, verified=False):
    user_id = str(user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if verified:
        keyboard.add(types.InlineKeyboardButton(text="Подтверждено ✅", callback_data="noAnswer"))
    else:
        keyboard.add(types.InlineKeyboardButton(text="Подтвердить", callback_data="verify:" + user_id))
    if not verified:
        keyboard.add(types.InlineKeyboardButton(text="Отказано ✅", callback_data="noAnswer"))
    else:
        keyboard.add(types.InlineKeyboardButton(text="Отказать", callback_data="unverify:" + user_id))
    tb.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)


def show_verification_request(message: types.Message, user_struct):
    text = "Ваша заявка на рассмотрении:\n\n" + user_struct["verification_request"]["about"] + "\n" + user_struct["verification_request"]["links"]
    tb.send_message(chat_id=message.chat.id, text=text)


def send_report_nm(message: types.Message, chat_id):
    tb.forward_message(chat_id, message.chat.id, message.message_id)
    text = "Удалить"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="delete_post:" + str(message.message_id)))
    keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data="nodelete_post:" + str(message.message_id)))
    tb.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

def report_was_sent(user_id: str or int):
    user_id = str(user_id)
    text = "Ваш жалоба учтена"
    tb.send_message(text=text, chat_id=user_id)


