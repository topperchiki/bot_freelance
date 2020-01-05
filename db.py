import psycopg2
from exceptions import FailedCallDatabase
from constants import DB_NAME, DB_USER, DB_HOST, DB_PASS


# decorator
def d_db_one(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        cursor.execute(*fn(*args, **kwargs))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if not result:
            raise FailedCallDatabase
        return result

    return f


# decorator
def d_db_all(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        cursor.execute(*fn(*args, **kwargs))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        if not result:
            raise FailedCallDatabase
        return result

    return f


# decorator
def d_db_empty(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        cursor.execute(*fn(*args, **kwargs))
        cursor.close()
        conn.commit()
        conn.close()

    return f


# decorator
def d_db_exist(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        cursor.execute(*fn(*args, **kwargs))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else ()

    return f


# decorator
def d_db_all_exist(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        cursor.execute(*fn(*args, **kwargs))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result if result else ()

    return f


@d_db_one
def user_posts(user_id: str):
    return "SELECT posts FROM posts WHERE owner_id = %s", (int(user_id),)


@d_db_one
def get_user_step(user_id: str or int):
    return "SELECT step FROM users WHERE user_id = %s", (int(user_id),)


@d_db_empty
def add_user(user_id: str or int, data_added: str or int):
    return "INSERT INTO users (user_id, date_added) VALUES (%s, %s)", \
           (int(user_id), str(data_added))


@d_db_empty
def set_prepare_user_categories(user_id: str or int, categories: str or int):
    return "UPDATE post_prepare SET categories = %s WHERE user_id = %s", \
           (str(categories), str(user_id))


@d_db_one
def get_prepare_user_categories(user_id: str or int):
    return "SELECT categories FROM post_prepare WHERE user_id = %s", \
           (str(user_id),)


@d_db_empty
def set_prepare_user_payment_type(user_id: str or int, pay_type: str or int):
    return "UPDATE post_prepare SET pay_type = %s WHERE user_id = %s", \
           (str(pay_type), str(user_id))


@d_db_empty
def set_prepare_user_guarantee(user_id: str or int, ans: bool):
    return "UPDATE post_prepare SET guarantee = %s WHERE user_id = %s", \
           (str(ans), str(user_id))


@d_db_empty
def set_prepare_user_portfolio(user_id: str or int, portfolio: str):
    return "UPDATE post_prepare SET portfolio = %s WHERE user_id = %s", \
           (str(portfolio), str(user_id))


@d_db_empty
def set_prepare_user_post_type(user_id: str or int, post_type: int or str):
    return "UPDATE post_prepare SET type = %s WHERE user_id = %s", \
           (str(post_type), str(user_id))


@d_db_empty
def clear_cache():
    return 0


@d_db_empty
def set_referral_code(referral_code: str, user_id: str or int):
    return "UPDATE referral_codes SET ref_code_text = %s " \
           "WHERE author_code_id = %s", (referral_code, str(user_id))


@d_db_empty
def set_used_referral_code(referral_code_id: str or int, user_id: str or int):
    return "UPDATE users SET referral_id = %s WHERE user_id = %s", \
           (str(referral_code_id), str(user_id))


@d_db_one
def get_used_referral_code(user_id: str or int):
    return "SELECT referral_id FROM users WHERE user_id = %s", (str(user_id),)


@d_db_all
def get_all_rates():
    return "SELECT rate_id, update_time, price, showed FROM rates"


@d_db_empty
def set_rate_show_status(rate_id: str or int, value: bool):
    return "UPDATE rates SET showed = %s WHERE rate_id = %s", \
           (str(value), str(rate_id))


@d_db_empty
def delete_rate(rate_id: str or int):
    return "DELETE FROM rates WHERE rate_id = %s", (str(rate_id),)


@d_db_empty
def clear_posts_rates(rate_id: str or int):
    return "UPDATE posts SET auto_ups = NULL, rate_id = NULL " \
           "WHERE rate_id = %s", (str(rate_id),)


@d_db_all
def get_all_posts_with_the_rate(rate_id: str or int):
    return "SELECT post_id FROM posts WHERE rate_id = %s", (str(rate_id),)


@d_db_empty
def clear_queue_with_the_rate(rate_id: str or int):
    return "DELETE FROM tasks WHERE rate_id = %s", (str(rate_id),)


@d_db_empty
def add_rate(rate_id: str or int, update_time: str or int,
             price: str or int):
    return "INSERT INTO rates(rate_id, update_time, price) " \
           "VALUES (%s, %s, %s)", \
           (str(rate_id), str(update_time), str(price))


@d_db_empty
def get_all_users():
    return ""


@d_db_empty
def set_user_ban_status(user_id: str or int, value: bool):
    return "UPDATE users SET banned = %s WHERE user_id = %s", \
           (str(value), str(user_id))


@d_db_empty
def set_verification_status(user_id: str or int, value: bool):
    return "UPDATE users SET verified = %s WHERE user_id = %s", \
           (str(value), str(user_id))


@d_db_empty
def delete_user_posts(user_id: str or int):
    return "DELETE FROM posts WHERE owner_id = %s", (str(user_id),)
    # TODO Очищать очередь от удаленных объявлений, удалять реферальные коды


@d_db_all_exist
def get_user_posts(user_id: str or int, start: int = 0, limit: int = 0):
    req = "SELECT post_id FROM posts WHERE owner_id = %s"
    if limit:
        req += "LIMIT " + str(limit)
    if start != 0:
        req += "OFFSET " + str(start)

    return req, (str(user_id),)


@d_db_one
def get_user_posts_count(user_id: str or int):
    return "SELECT posts_count FROM users WHERE user_id = %s", \
           (str(user_id),)


@d_db_empty
def set_user_step(user_id: str or int, step: int or str):
    return "UPDATE users SET step = %s WHERE user_id = %s", \
           (str(step), str(user_id))


@d_db_all_exist
def get_count_user_posts(user_id: str or int):
    return "SELECT post_id FROM posts WHERE owner_id = %s", (str(user_id),)


@d_db_one
def get_post_info(post_id: str or int):
    # type, title, category, time_last_up, rate_id, auto_ups
    return "SELECT type, title, categories, last_up, rate_id, auto_ups, auto_ups_used " \
           "FROM posts WHERE post_id = %s", \
           (str(post_id),)


@d_db_one
def get_category_hashtag(category_id: str or int):
    return "SELECT hashtag FROM categories WHERE category_id = %s", \
           (str(category_id),)


@d_db_one
def get_rate_time(rate_id: str or int):
    return "SELECT update_time FROM rates WHERE rate_id = %s", (str(rate_id), )


@d_db_one
def get_user_manual_ups(user_id: str or int):
    return "SELECT manual_ups FROM users WHERE user_id = %s", \
           (str(user_id),)


@d_db_all_exist
def get_category_children_if_exists(category_id: str or int):
    return "SELECT category_id FROM categories WHERE category_parent = %s", \
           (str(category_id),)


@d_db_one
def get_category_name(category_id: str or int):
    return "SELECT name FROM categories WHERE category_id = %s", \
           (str(category_id),)


@d_db_empty
def set_post_last_up(post_id: str or int, update_time: str or int):
    return "UPDATE posts SET last_up = %s WHERE post_id = %s", \
           (str(update_time), str(post_id))


@d_db_all_exist
def get_available_auto_actions(time_to_check: int or str):
    return "SELECT action_type, post_id, counts, " \
           "plus_time, rate_id, message_id, maxcount FROM auto_actions " \
           "WHERE time_to_do < %s", \
           (str(int(time_to_check)),)


@d_db_empty
def set_next_post_up_in_auto_post(post_id: str or int,
                                  counts: int or str, new_time: int or str):
    return "UPDATE auto_actions SET counts = %s, " \
           "time_to_do = %s WHERE post_id = %s", \
           (str(counts), str(new_time), str(post_id))


@d_db_empty
def set_time_to_do_auto_post(post_id: str or int, new_time: int or str):
    return "UPDATE auto_actions SET time_to_do = %s WHERE post_id = %s", \
           (str(new_time), str(post_id))


@d_db_empty
def delete_auto_action_with_post_id(post_id: str or int):
    return "DELETE FROM auto_actions WHERE post_id = %s", (str(post_id),)


@d_db_empty
def delete_auto_action_with_message_id(message_id: str or int):
    return "DELETE FROM auto_actions WHERE message_id = %s", (str(message_id),)


@d_db_empty
def set_post_last_up_and_used_counts(post_id: str or int,
                                update_time: str or int, auto_ups_used: str or int):
    return "UPDATE posts SET last_up = %s, auto_ups_used = %s WHERE post_id = %s", \
           (str(update_time), str(auto_ups_used), str(post_id))


@d_db_empty
def add_auto_actions_task(act_type: int, time_to_do, post_id: str or int=0, plus_time=0,
                          rate_id=0, message_id=0, maxcount=0):
    return "INSERT INTO auto_actions(action_type, time_to_do, " \
           "post_id, plus_time, rate_id, message_id, maxcount) VALUES " \
           "(%s, %s, %s, %s, %s, %s, %s)", \
           (str(act_type), str(time_to_do), str(post_id), str(plus_time),
            str(rate_id), str(message_id), str(maxcount))


@d_db_empty
def set_user_verification_status(user_id: str or int, value: bool):
    return "UPDATE users SET verified = %s WHERE user_id = %s", \
           (str(value), str(user_id))


@d_db_one
def get_user_verification_status(user_id: str or int):
    return 'SELECT verified FROM users WHERE user_id = %s', \
           (str(user_id),)


@d_db_one
def get_info_about_user_ban(user_id: str or int):
    return 'SELECT banned, notified_ban FROM users WHERE user_id = %s', \
           (str(user_id),)


@d_db_exist
def get_user_step_ban_status_is_admin(user_id: str or int):
    return 'SELECT step, banned, notified_ban, admin FROM users ' \
           'WHERE user_id = %s', \
           (str(user_id), )


@d_db_empty
def set_user_notified_ban(user_id: str or int, status: bool):
    return 'UPDATE users SET notified_ban = %s WHERE user_id = %s', \
           (str(status), str(user_id),)


@d_db_empty
def set_user_referral_code(user_id: str or int, author_user_id: str or int):
    return 'UPDATE users SET referral_id = %S WHERE user_id = %s', \
           (str(author_user_id), str(user_id),)


@d_db_one
def get_info_referral_code(referral_code: str or int):
    return 'SELECT ref_code_id, count, author_code_id FROM referral_codes ' \
           'WHERE ref_code_text = %s', \
           (str(referral_code),)


@d_db_all_exist
def get_categories_ids_names_with_parent(parent_id: str or int):
    return 'SELECT category_id, name FROM categories ' \
           'WHERE category_parent = %s', \
           (str(parent_id),)


@d_db_one
def get_category_parent(category_id: str or int):
    return 'SELECT category_parent FROM categories WHERE category_id = %s', \
           (str(category_id),)


@d_db_exist
def get_category_parent_if_exists(category_id: str or int):
    return 'SELECT category_parent FROM categories WHERE category_id = %s', \
           (str(category_id),)


@d_db_empty
def add_category(category_id: str or int, name: str, hashtag: str):
    return 'INSERT INTO categories(category_id, name, hashtag) ' \
           'VALUES (%s, %s, %s)', (str(category_id), str(name), str(hashtag))


@d_db_empty
def set_category_parent(category_id: int or str,
                        parent_category_id: str or int):
    return 'UPDATE categories SET category_parent = %s ' \
           'WHERE category_id = %s', \
           (str(parent_category_id), str(category_id),)


@d_db_exist
def is_prepare_exist(user_id: str or int):
    return 'SELECT user_id FROM post_prepare WHERE user_id = %s', \
           (str(user_id),)


@d_db_empty
def add_prepare_post(user_id: str or int):
    return 'INSERT INTO post_prepare(user_id) VALUES (%s)', (str(user_id),)


@d_db_empty
def set_prepare_user_title(user_id: str or int, title: str):
    return 'UPDATE post_prepare SET title = %s WHERE user_id = %s', \
           (title, str(user_id),)


@d_db_empty
def set_prepare_user_description(user_id: str or int, description: str):
    return 'UPDATE post_prepare SET description = %s WHERE user_id = %s', \
           (description, str(user_id),)


@d_db_empty
def set_prepare_user_memo(user_id: str or int, memo: str):
    return 'UPDATE post_prepare SET memo = %s WHERE user_id = %s', \
           (memo, str(user_id),)


@d_db_empty
def set_prepare_user_contacts(user_id: str or int, contacts: str):
    return 'UPDATE post_prepare SET contacts = %s WHERE user_id = %s', \
           (contacts, str(user_id),)


@d_db_empty
def set_prepare_user_price(user_id: str or int, price: str):
    return 'UPDATE post_prepare SET price = %s WHERE user_id = %s', \
           (price, str(user_id),)


@d_db_one
def get_prepare_user_price(user_id):
    return 'SELECT price FROM post_prepare WHERE user_id = %s', (str(user_id),)


@d_db_exist
def is_category_exist(category_id: str or int):
    return 'SELECT category_id FROM categories WHERE category_id = %s', \
           (str(category_id),)


@d_db_one
def get_user_code(user_id: str or int):
    return "SELECT ref_code_text FROM referral_codes WHERE " \
           "author_code_id = %s", \
           (str(user_id),)


@d_db_one
def get_referral_code_info(code: str):
    return "SELECT author_code_id, count FROM referral_codes " \
           "WHERE ref_code_text = %s", \
           (code,)


@d_db_empty
def set_ban_status(user_id: str or int, value: bool):
    return "UPDATE users SET banned = %s WHERE user_id = %s", \
           (str(user_id), str(value))


@d_db_one
def get_ban_info(user_id: str or int):
    return "SELECT banned, notified_ban FROM users WHERE user_id = %s", \
           (str(user_id),)


@d_db_empty
def set_manual_ups(user_id: str or int, manual_ups: str or int):
    return "UPDATE users SET manual_ups = %s WHERE user_id = %s", \
           (str(manual_ups), str(user_id))


@d_db_one
def get_manual_ups(user_id: str or int):
    return "SELECT manual_ups FROM users WHERE user_id = %s", \
           (str(user_id),)


@d_db_empty
def set_notified_ban_status(user_id: str or int, notified_ban: bool):
    return "UPDATE users SET notified_ban = %s WHERE user_id = %s", \
           (str(notified_ban), str(user_id))


@d_db_empty
def set_referral_code_user_count(user_id: str or int, count: int or str):
    return "UPDATE referral_codes SET count = %s WHERE author_code_id = %s", \
           (str(count), str(user_id))


@d_db_empty
def set_auto_ups_count(post_id: str or int, count: str or int):
    return "UPDATE posts SET auto_ups = %s WHERE post_id = %s", \
           (str(count), str(post_id))


@d_db_empty
def delete_post(post_id: str or int):
    return "DELETE FROM posts WHERE post_id = %s", (str(post_id),)


@d_db_empty
def delete_auto_action_post(post_id: str or int):
    return "DELETE FROM posts WHERE post_id = %s and action_type = 1", \
           (str(post_id),)


@d_db_all_exist
def get_user_posts_from_to(user_id: str or int,
                           skip: str or int, count: str or int):
    return "SELECT post_id FROM posts WHERE user_id = %s LIMIT %s, %s", \
           (str(user_id), str(skip), str(count))


@d_db_one
def get_prepared_post(user_id: str or int):
    return "SELECT type, title, description, categories, memo, portfolio, " \
           "contacts, pay_type, price, guarantee " \
           "FROM post_prepare WHERE user_id = %s", \
           (str(user_id),)


@d_db_all
def get_hashtags_categories_with_ids(categories_ids: tuple or list):
    command = "SELECT category_id, hashtag FROM categories WHERE category_" \
              "id IN ( " + "%s, " * len(categories_ids)
    command = command[:-2]
    pack = list([str(i) for i in categories_ids])
    return command + ")", pack


@d_db_one
def get_prepare_new_user_categories(user_id: str or int):
    return "SELECT new_categories FROM post_prepare WHERE user_id = %s", \
           (str(user_id),)


@d_db_empty
def set_prepare_new_user_categories(user_id: str or int,
                                    categories: str or int):
    return "UPDATE post_prepare SET new_categories = %s WHERE user_id = %s", \
           (str(categories), str(user_id))


@d_db_empty
def set_prepare_payment_info(user_id: str or int, pay_type: str or int, price: str or int):
    return "UPDATE post_prepare SET pay_type = %s, price = %s " \
           "WHERE user_id = %s", \
           (str(pay_type), str(price), str(user_id))


@d_db_empty
def set_prepare_new_user_price(user_id: str or int, price: str or int):
    return "UPDATE post_prepare SET new_prices = %s WHERE user_id = %s", \
           (str(price), str(user_id))


@d_db_one
def get_prepare_new_user_price(user_id: str or int):
    return "SELECT new_prices FROM post_prepare WHERE user_id = %s", \
           (str(user_id), )


@d_db_one
def get_prepare_post_type(user_id: str or int):
    return "SELECT type FROM post_prepare WHERE user_id = %s", (str(user_id), )


@d_db_one
def get_user_info(user_id: str or int):
    return "SELECT user_id, user_posts_count, manual_ups, spent_money, " \
           "verified, referral_id, referral_author, banned, " \
           "notified_ban FROM users WHERE user_id = %s", (str(user_id), )


@d_db_one
def get_post(post_id: str or int):
    return "SELECT type, title, description, memo, portfolio, contacts, " \
           "pay_type, price, guarantee, categories " \
           "FROM posts WHERE post_id = %s", \
           (str(post_id),)


@d_db_one
def get_rate_info(rate_id: str or int):
    return "SELECT update_time, price, showed FROM rates " \
           "WHERE rate_id = %s", (str(rate_id), )


@d_db_empty
def add_rate(rate_id: str or int, update_time: str or int, price: str or int,
             showed: bool=False):
    return "INSERT INTO rates (rate_id, update_time, price, showed) " \
           "VALUES (%s, %s, %s, %s)", \
           (str(rate_id), str(update_time), str(price), str(showed))


@d_db_empty
def set_rate_showed_status(rate_id: str or int, value: bool):
    return "UPDATE rates SET showed = %s WHERE rate_id = %s", \
           (str(rate_id), str(value))


@d_db_one
def get_prepare_post_all(user_id: str or int):
    return "SELECT type, title, description, memo, portfolio, contacts, " \
           "categories, price, pay_type, guarantee " \
           "FROM post_prepare WHERE user_id = %s", \
           (str(user_id), )


@d_db_empty
def add_post(post_id: str or int, user_id: str or int,
             creation_date: int or str,  last_up: str or int,
             post_type: int or str, title: str, description: str, memo: str,
             portfolio: str, contacts: str, categories: str, price: str,
             pay_type: str, guarantee: bool):
    return "INSERT INTO posts(post_id, owner_id, creation_date, last_up, " \
           "type, title, description, memo, portfolio, contacts, categories, " \
           "price, pay_type, guarantee) " \
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",\
           (str(post_id), str(user_id), str(creation_date), str(last_up),
            str(post_type), title, description, memo, portfolio, contacts, categories,
            price, str(pay_type), str(guarantee))


@d_db_exist
def is_post_id_exist(post_id: int or str):
    return "SELECT post_id FROM posts WHERE post_id = %s", (str(post_id), )


@d_db_one
def get_post_owner_id(post_id: str or int):
    return "SELECT owner_id FROM posts WHERE post_id = %s", (str(post_id), )


@d_db_exist
def get_post_owner_id_if_exists(post_id: str or int):
    return "SELECT owner_id FROM posts WHERE post_id = %s", (str(post_id), )


@d_db_exist
def get_post_owner_id_and_last_up_and_rate_id_if_exists(post_id: str or int):
    return "SELECT owner_id, last_up, rate_id FROM posts WHERE post_id = %s", \
           (str(post_id), )


@d_db_one
def get_post_all(post_id: str or int):
    return "SELECT type, title, description, memo, portfolio, contacts, " \
           "categories, price, pay_type, guarantee, creation_date, last_up, " \
           "auto_ups, auto_ups_used, rate_id, owner_id " \
           "FROM posts WHERE post_id = %s", \
           (str(post_id),)


@d_db_one
def get_prepare_payment_info(user_id: str or int):
    return "SELECT pay_type, price FROM post_prepare WHERE user_id = %s", \
           (str(user_id), )


@d_db_one
def get_user_posts_count(user_id: str or int):
    return 'SELECT posts_count FROM users WHERE user_id = %s', \
           (str(user_id),)


@d_db_empty
def set_user_posts_count(user_id: str or int, value: int or str):
    return 'UPDATE users SET posts_count = %s WHERE user_id = %s', \
           (str(value), str(user_id))


@d_db_empty
def set_admin_status(user_id: str or int, value: bool):
    return 'UPDATE users SET admin = %s WHERE user_id = %s', \
           (str(value), str(user_id))


@d_db_exist
def get_admin_status_if_exists(user_id: str or int):
    return 'SELECT admin FROM users WHERE user_id = %s', (str(user_id), )


@d_db_one
def get_verification_ticket_text_and_status(user_id: str or int):
    return 'SELECT text, status FROM vtickets WHERE user_id = %s', \
           (str(user_id), )


@d_db_one
def get_verification_ticket_contacts_and_status(user_id: str or int):
    return 'SELECT contacts, status FROM vtickets WHERE user_id = %s', \
           (str(user_id), )


@d_db_one
def get_verification_ticket_status(user_id: str or int):
    return 'SELECT status FROM vtickets WHERE user_id = %s', (str(user_id),)


@d_db_empty
def set_verification_ticket(user_id: str or int, text: str,
                            contacts: str, status: int or str):
    return 'UPDATE vtickets SET text = %s, contacts = %s, ' \
           'status = %s WHERE user_id = %s', \
           (text, contacts, str(status), str(user_id))


@d_db_empty
def set_verification_ticket_status(user_id: str or int, status: int or str):
    return 'UPDATE vtickets SET status = %s WHERE user_id = %s', \
           (str(status), str(user_id))


@d_db_one
def get_verification_ticket_text_and_contacts(user_id: str or int):
    return 'SELECT text, contacts FROM vtickets WHERE user_id = %s', (str(user_id), )


@d_db_empty
def add_row_to_vtickets(user_id: str or int):
    return 'INSERT INTO vtickets(user_id, text, contacts, status) ' \
           'VALUES (%s, \'\', \'\', 0)', \
           (str(user_id), )


@d_db_empty
def set_verification_text(user_id: str or int, text: str):
    return 'UPDATE vtickets SET text = %s WHERE user_id = %s', \
           (str(text), str(user_id))


@d_db_empty
def set_verification_contacts(user_id: str or int, contacts: str):
    return 'UPDATE vtickets SET contacts = %s WHERE user_id = %s', \
           (str(contacts), str(user_id))


@d_db_all_exist
def get_showed_rates():
    return 'SELECT rate_id, update_time, price FROM rates ' \
           'WHERE showed = True', \
           None


@d_db_exist
def get_rate_time_and_price_if_exist(rate_id: str or int):
    return 'SELECT update_time, price FROM rates WHERE rate_id = %s', \
           (str(rate_id), )


@d_db_exist
def get_rate_price_if_exist(rate_id: str or int):
    return 'SELECT price FROM rates WHERE rate_id = %s', \
           (str(rate_id), )


@d_db_exist
def get_rate_time_if_exist(rate_id: str or int):
    return 'SELECT update_time FROM rates WHERE rate_id = %s', \
           (str(rate_id), )


@d_db_empty
def set_user_chose_rate_and_post_to(user_id: str or int,
                                    rate_id: str or int, post_id: str or int):
    return 'UPDATE users SET chose_rate = %s, post_to = %s WHERE user_id = %s', \
           (str(rate_id), str(post_id), str(user_id))


@d_db_one
def get_user_chose_rate_and_post_to(user_id: str or int):
    return 'SELECT chose_rate, post_to FROM users WHERE user_id = %s', \
           (str(user_id), )


@d_db_one
def get_post_rate(post_id: str or int):
    return "SELECT rate_id FROM posts WHERE post_id = %s", (str(post_id),)


@d_db_empty
def set_post_auto_ups_info(post_id: str or int,
                           rate_id: str or int, ups: str or int):
    return "UPDATE posts SET rate_id = %s, " \
           "auto_ups = %s, auto_ups_used = 0 WHERE post_id = %s", \
           (str(rate_id), str(ups), str(post_id))



# TODO  reports db
# @d_db_exist
# def get_user_report_if_exist(user_id: str or int, post_id: str or int):
#     return 'SELECT user_id FROM reports WHERE user_id = %s, ' \
#            'post_id = %s', \
#            (str(user_id), str(post_id))
#
#
# @d_db_empty
# def add_user_report(user_id: str or int, post_id: str or int):
#     return 'INSERT INTO reports(user_id, post_id) VALUES (%s, %s)',
#             (str(user_id), str(post_id))
#
#
# @d_db_empty
# def del_user_report(user_id: str or int, post_id: str or int):
#     return "DELETE FROM reports WHERE user_id = %s, post_id = %s", \
#            (str(user_id), str(post_id))
#
#
# @d_db_empty
# def set_post_reports(post_id: str or int, reports: int or str):
#     return 'UPDATE posts SET reports = %s WHERE post_id = %s', \
#            (str(reports), str(post_id))
#
#
# @d_db_empty
# def set_post_reports_and_sent_status(post_id: str or int, reports: int or str, status: bool):
#     return 'UPDATE posts SET reports = %s, report_was_sent = %s WHERE post_id = %s', \
#            (str(reports), str(status), str(post_id))
#
#
# @d_db_one
# def get_post_reports(post_id: str or int):
#     return 'SELECT reports FROM posts WHERE post_id = %s', \
#            (str(post_id), )
#
# @d_db_empty
# def del_all_post_report(post_id: str or int):
#     return "DELETE FROM reports WHERE post_id = %s", \
#            (str(post_id))
