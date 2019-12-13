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
    return "SELECT posts FROM posts WHERE owner_id = %s", (int(user_id), )


@d_db_one
def get_user_step(user_id: str or int):
    return "SELECT step FROM users WHERE user_id = %s", (int(user_id), )


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
           (str(user_id), )


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
    return "SELECT referral_id FROM users WHERE user_id = %s", (str(user_id), )


@d_db_all
def get_all_rates():
    return "SELECT rate_id, update_time, price, showed FROM rates"


@d_db_empty
def set_rate_show_status(rate_id: str or int, value: bool):
    return "UPDATE rates SET show = %s WHERE rate_id = %s", \
           (str(rate_id), str(value))


@d_db_empty
def delete_rate(rate_id: str or int):
    return "DELETE FROM rates WHERE rate_id = %s", (str(rate_id), )


@d_db_empty
def clear_posts_rates(rate_id: str or int):
    return "UPDATE posts SET auto_ups = NULL, auto_ups_type = NULL " \
           "WHERE auto_ups_type = %s", (str(rate_id), )


@d_db_all
def get_all_posts_with_the_rate(rate_id: str or int):
    return "SELECT post_id FROM posts WHERE auto_ups_type = %s", (str(rate_id),)


@d_db_empty
def clear_queue_with_the_rate(rate_id: str or int):
    return "DELETE FROM tasks WHERE rate_id = %s", (str(rate_id), )


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
           str(value), str(user_id)


@d_db_empty
def delete_user_posts(user_id: str or int):
    return "DELETE FROM posts WHERE owner_id = %s", (str(user_id), )
    #TODO Очищать очередь от удаленных объявлений, удалять реферальные коды


@d_db_all_exist
def get_user_posts(user_id: str or int):
    return "SELECT user_posts_count FROM users WHERE user_id = %s", \
           (str(user_id), )


@d_db_exist
def get_user_steps_if_exists(user_id: str or int):
    return "SELECT step FROM users WHERE user_id = %s", (str(user_id), )
    

@d_db_empty
def set_user_step(user_id: str or int, step: int or str):
    return "UPDATE users SET step = %s WHERE user_id = %s", \
           (str(step), str(user_id))


@d_db_all_exist
def get_count_user_posts(user_id: str or int):
    return "SELECT post_id FROM posts WHERE owner_id = %s", (str(user_id), )


@d_db_one
def get_post_info(post_id: str or int):
    # type, title, category, time_last_up, rate_id, auto_ups
    return "SELECT type, title, categories, last_up, rate_id, auto_ups " \
           "FROM posts WHERE post_id = %s", \
           (str(post_id), )


@d_db_one
def get_category_hashtag(category_id: str or int):
    return "SELECT hashtag FROM categories WHERE category_id = %s", \
           (str(category_id), )


@d_db_one
def get_rate_time(rate_id: str or int):
    return 0


@d_db_one
def get_user_manual_ups(user_id: str or int):
    return "SELECT manual_ups FROM users WHERE user_id = %s", \
           (str(user_id), )


@d_db_all_exist
def get_category_children_if_exists(category_id: str or int):
    return "SELECT category_id FROM categories WHERE category_parent = %s", \
           (str(category_id), )


@d_db_one
def get_category_name(category_id: str or int):
    return "SELECT name FROM categories WHERE category_id = %s", \
           (str(category_id), )


@d_db_empty
def set_post_last_up(post_id: str or int, update_time: str or int):
    return "UPDATE posts SET last_up = %s WHERE post_id = %s", \
           (str(update_time), str(post_id))


@d_db_all_exist
def get_available_auto_actions(time_to_check: int or str):
    return "SELECT action_type, post_id, counts, " \
           "plus_time, rate_id, message_id FROM auto_actions " \
           "WHERE time_to_do < %s", \
           (str(int(time_to_check)),)


@d_db_empty
def set_next_post_up_in_auto_post(post_id: str or int,
                                  counts: int or str, new_time: int or str):
    return "UPDATE auto_actions SET count = %s, " \
           "time_to_do = %s WHERE post_id = %s", \
           (str(counts), str(new_time), str(post_id))


@d_db_empty
def delete_auto_action_with_post_id(post_id: str or int):
    return "DELETE FROM auto_actions WHERE post_id = %s", (str(post_id), )


@d_db_empty
def delete_auto_action_with_message_id(message_id: str or int):
    return "DELETE FROM auto_actions WHERE message_id = %s", (str(message_id), )


@d_db_empty
def set_post_last_up_and_counts(post_id: str or int,
                                update_time: str or int, auto_ups: str or int):
    return "UPDATE posts SET last_up = %s, auto_ups = %s WHERE post_id = %s", \
           (str(update_time), str(post_id), str(auto_ups))


@d_db_empty
def set_user_verification_status(user_id: str or int, value: bool):
    return "UPDATE users SET verified = %s WHERE user_id = %s", \
           (str(value), str(user_id))


@d_db_one
def get_user_verification_status(user_id: str or int):
    return 'SELECT verified FROM users WHERE user_id = %s', \
           (str(user_id), )


@d_db_one
def get_info_about_user_ban(user_id: str or int):
    return 'SELECT banned, notified_ban FROM users WHERE user_id = %s', \
           (str(user_id), )


@d_db_empty
def set_user_notified_ban(user_id: str or int, status: bool):
    return 'UPDATE users SET notified_ban = %s WHERE user_id = %s', \
           (str(status), str(user_id), )


@d_db_empty
def set_user_referral_code(user_id: str or int, author_user_id: str or int):
    return 'UPDATE users SET referral_id = %S WHERE user_id = %s', \
           (str(author_user_id), str(user_id), )


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
           (str(category_id), )


@d_db_empty
def add_category(category_id: str or int, name: str, hashtag: str):
    return 'INSERT INTO categories(category_id, name, hashtag) ' \
           'VALUES (%s, %s, %s)', (str(category_id), str(name), str(hashtag))


@d_db_empty
def set_category_parent(category_id: int or str,
                        parent_category_id: str or int):
    return 'UPDATE categories SET category_parent = %s ' \
           'WHERE category_id = %s', \
           (str(parent_category_id), str(category_id), )


@d_db_exist
def is_prepare_exist(user_id: str or int):
    return 'SELECT user_id FROM post_prepare WHERE user_id = %s', \
           (str(user_id), )


@d_db_empty
def add_prepare_post(user_id: str or int):
    return 'INSERT INTO post_prepare(user_id) VALUES (%s)', (str(user_id), )


@d_db_empty
def set_prepare_user_title(user_id: str or int, title: str):
    return 'UPDATE post_prepare SET title = %s WHERE user_id = %s', \
           (title, str(user_id), )


@d_db_empty
def set_prepare_user_description(user_id: str or int, description: str):
    return 'UPDATE post_prepare SET description = %s WHERE user_id = %s', \
           (description, str(user_id), )


@d_db_empty
def set_prepare_user_memo(user_id: str or int, memo: str):
    return 'UPDATE post_prepare SET memo = %s WHERE user_id = %s', \
           (memo, str(user_id), )


@d_db_empty
def set_prepare_user_contacts(user_id: str or int, contacts: str):
    return 'UPDATE post_prepare SET contacts = %s WHERE user_id = %s', \
           (contacts, str(user_id), )


@d_db_empty
def set_prepare_user_price(user_id: str or int, price: str):
    return 'UPDATE post_prepare SET price = %s WHERE user_id = %s', \
           (price, str(user_id), )


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
           "author_code_id = %s", (str(user_id), )


@d_db_one
def get_referral_code_info(code: str):
    return "SELECT author_code_id, count FROM referral_codes " \
           "WHERE ref_code_text = %s", (code, )


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
def get_manual_ups(user_id: str or int, manual_ups: str or int):
    return "SELECT manual_ups FROM users WHERE user_id = %s", \
           (str(manual_ups), str(user_id))


@d_db_empty
def set_notified_ban_status(user_id: str or int, notified_ban: bool):
    return "UPDATE users SET notified_ban = %s WHERE user_id = %s", \
           (str(notified_ban), str(user_id))


@d_db_empty
def set_referral_code_user_count(user_id: str or int, count: int or str):
    return "UPDATE referral_codes SET count = %s WHERE author_code_id = %s", \
           (str(count), str(user_id))
