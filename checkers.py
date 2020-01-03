from constants import *

import re


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
