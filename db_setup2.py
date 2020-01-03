import psycopg2
import db
import json


def create_verification_tickets_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE vtickets(
                                user_id INT NOT NULL,
                                status INT DEFAULT 1, 
                                text TEXT,
                                contacts TEXT
                                )''')
    cursor.close()

# 0 0 0 0 0 0
# 1 - Filled text
# 2 - Filled contacts
# 3 - Paid
# 4 - Sent
# 5 - Checked by admins
# 6 - Approved or no
# 7 - Verified by admin


def create_auto_actions_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE auto_actions(
                                action_type INT NOT NULL,
                                time_to_do INT NOT NULL,
                                post_id INT,
                                counts INT,
                                plus_time INT,
                                rate_id INT,
                                message_id INT
                                )''')
    cursor.close()


def create_post_prepare_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE post_prepare(
                                user_id INT UNIQUE NOT NULL,
                                type INT NOT NULL DEFAULT 1,
                                title VARCHAR(50),
                                description VARCHAR(50), 
                                memo VARCHAR(350),
                                portfolio TEXT,
                                contacts VARCHAR(100),
                                categories TEXT,
                                price TEXT,
                                pay_type INT,
                                guarantee BOOLEAN,

                                new_categories TEXT,
                                new_prices TEXT
                                )''')
    cursor.close()


def create_categories_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE categories(
                                category_id INT UNIQUE NOT NULL,
                                category_parent INT NOT NULL DEFAULT 0,
                                children_count INT NOT NULL DEFAULT 0,
                                name VARCHAR(50),
                                hashtag VARCHAR(50)
                                )''')
    cursor.close()


def create_referral_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE referral_codes(
                                author_code_id INT UNIQUE NOT NULL,
                                ref_code_text VARCHAR(30) UNIQUE,
                                count INT DEFAULT 0
                                )''')
    cursor.close()


def create_rates_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE rates(
                                rate_id INT UNIQUE NOT NULL,
                                update_time INT NOT NULL,
                                price INT NOT NULL,
                                showed BOOLEAN NOT NULL DEFAULT FALSE
                                )''')
    cursor.close()


def create_posts_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE posts(
                               post_id INT UNIQUE NOT NULL,
                               owner_id INT NOT NULL,
                               creation_date INT NOT NULL,
                               type INT NOT NULL,

                               title VARCHAR(50),
                               description VARCHAR(50),
                               memo VARCHAR(350),
                               portfolio TEXT,
                               contacts VARCHAR(100),
                               categories TEXT,
                               price TEXT,
                               pay_type INT, 
                               guarantee BOOLEAN,

                               auto_ups INT DEFAULT 0,
                               auto_ups_used INT DEFAULT 0,
                               rate_id INT DEFAULT 0,
                               last_up INT DEFAULT 0,

                               reported INT DEFAULT 0,
                               users_reported TEXT,
                               report_was_sent BOOLEAN DEFAULT FALSE
                                )''')
    cursor.close()


def create_users_table(connection: psycopg2.extensions.connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE users(
                                user_id INT UNIQUE NOT NULL,
                                date_added INT NOT NULL,

                                step INT NOT NULL DEFAULT 0,
                                admin BOOLEAN NOT NULL DEFAULT FALSE,
                                posts_count INT NOT NULL DEFAULT 0,
                                manual_ups INT NOT NULL DEFAULT 0,
                                spent_money INT NOT NULL DEFAULT 0,
                                verified BOOLEAN NOT NULL DEFAULT FALSE,
                                referral_id INT,
                                referral_author INT,
                                banned BOOLEAN NOT NULL DEFAULT FALSE,
                                notified_ban BOOLEAN NOT NULL DEFAULT FALSE,
                                chose_rate INT,
                                post_to INT
                                )''')
    cursor.close()


def run_command(connection: psycopg2.extensions.connection, command):
    cursor = connection.cursor()
    cursor.execute(command)
    cursor.close()
    connection.commit()


def main_setup(db_name, db_user, db_pass, db_host="localhost"):
    conn = psycopg2.connect(dbname=db_name, user=db_user,
                            password=db_pass, host=db_host)
    need = input("Do you need tables? [y/n]")
    if need.lower() == "y" or need.lower() == "yes":
        print("Creating...")

        create_users_table(conn)
        create_posts_table(conn)
        create_rates_table(conn)
        create_referral_table(conn)
        create_auto_actions_table(conn)
        create_categories_table(conn)
        create_post_prepare_table(conn)
        create_verification_tickets_table(conn)
        conn.commit()
        run_command(conn, "ALTER TABLE \"post_prepare\" "
                          "ALTER COLUMN \"categories\" SET DEFAULT '';")
        run_command(conn, "ALTER TABLE \"post_prepare\" "
                          "ALTER COLUMN \"new_categories\" SET DEFAULT '';")
        conn.close()
        print("Success")

    need = input("Do you need categories? [y/n]")
    if need.lower() == "y" or need.lower() == "yes":
        try:
            with open('categories.json') as f1:
                d1 = json.loads(f1.read())
            with open('categories_r.json') as f2:
                d2 = json.loads(f2.read())
        except (FileExistsError, FileNotFoundError):
            print("No necessary files")

        else:
            for category in d1.items():
                db.add_category(category[0], category[1]["name"],
                                category[1]["hashtag"])

            for category in d2.items():
                db.set_category_parent(category[0], category[1]["parent"])


if __name__ == "__main__":
    from constants import DB_NAME, DB_HOST, DB_PASS, DB_USER

    main_setup(DB_NAME, DB_USER, DB_PASS, DB_HOST)
