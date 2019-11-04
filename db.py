import psycopg2
from constants import DB_NAME, DB_USER, DB_HOST, DB_PASS


# decorator
def d_db_one(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        fn(*args, **kwargs)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return (True, result[0]) if result else (False,)

    return f


# decorator
def d_db_all(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        fn(*args, **kwargs)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return (True, result) if result else (False,)
    return f


# decorator
def d_db_empty(fn):
    def f(*args, **kwargs):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        fn(*args, **kwargs)
        cursor.close()
        conn.close()
    return f


@d_db_one
def user_posts(user_id: str):
    global cursor
    cursor.execute("SELECT posts FROM ownerships WHERE user_id = %s", (str(user_id)))


@d_db_one
def get_user_step(user_id: str):
    global cursor
    cursor.execute("SELECT step FROM ownerships WHERE user_id = %s", (str(user_id)))


@d_db_empty
def add_user(user_id: str):
    global cursor
    cursor.execute("INSERT INTO users(user_id) VALUES (%s)", (str(user_id)))


@d_db_one
def get_category_children(category_id: str or int):
    global cursor
    cursor.execute("SELECT children FROM categories_r WHERE categories_id = %s", (str(category_id)))


@d_db_one
def get_user_categories(user_id: str or int):
    global cursor
    cursor.execute("SELECT categories FROM users WHERE user_id = %s", (str(user_id)))


@d_db_one
def set_user_categories(user_id: str or int, categories: str or int):
    global cursor
    cursor.execute("UPDATE users SET categories = %s WHERE user_id = %s", (str(categories), str(user_id)))


@d_db_one
def get_category_info(category_id: str or int):
    global cursor
    cursor.execute("SELECT category_name FROM categories WHERE category_id = %s", (str(category_id)))


