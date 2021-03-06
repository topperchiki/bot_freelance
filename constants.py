# Telegram info
TOKEN = '825727999:AAGTZPK2TRRWZID-rxXicGpFeAbd8dbMyrk'
BOT_USERNAME = "bot_username"
CONTACT_ACC_USERNAME = "google"
ID_POST_CHANNEL = -243828263
USERNAME_POST_CHANNEL = ""
ID_MANAGE_CHANNEL = -243828263
ALLOWED_GROUP_CHATS = {ID_POST_CHANNEL, ID_MANAGE_CHANNEL}

# Payment
PAYMENT_PROVIDER = '410694247:TEST:1496cc79-d856-44c4-9aa0-0271d717ca9f'
MANUAL_UPS_PRICE = 50

# Files' path
P_ACTIONS = "./data/actions.txt"

# Other limits
EDITING_DELAY = 86400

# Letters limits
FREELANCE_TITLE_LETTERS_LIMIT = 50
FREELANCE_DESCRIPTION_LETTERS_LIMIT = 500
FREELANCE_MEMO_LETTERS_LIMIT = 350
FREELANCE_CONTACTS_LETTERS_LIMIT = 100
CUSTOMER_TITLE_LETTERS_LIMIT = 50
CUSTOMER_DESCRIPTION_LETTERS_LIMIT = 500
CUSTOMER_MEMO_LETTERS_LIMIT = 350
CUSTOMER_CONTACTS_LETTERS_LIMIT = 100
VERIFICATION_ABOUT_LETTERS_LIMIT = 500
VERIFICATION_LINKS_LETTERS_LIMIT = 500


# db info
DB_NAME = 'test_db'
DB_USER = 'postgres'
DB_HOST = '127.0.0.1'
DB_PASS = '123456'
OUTPUT_PATH = ''

# text
T_COMPLETE_EDITING = "Закончите редактирование"
T_HELP = "Этот бот для канала " + ("@" + USERNAME_POST_CHANNEL if USERNAME_POST_CHANNEL else "с фриланс-работой") \
         + ".\n\n/start - Вызвать начальное меню\n/myposts - Мои объявления\n\nЧтобы подать объявление нужно:\n" \
           "1. В главном меню выбрать \"Новое объявление\"\n2. Выбрать исполнитель вы или заказчик\n" \
           "3. Заполнить необходимые сведения\n4. Нажать кнопку \"Опубликовать\"\n\nОпубликованное объявление " \
           "можно \"поднимать\". Для этого вы можете приобрести ручные подъемы (частота поднятия не чаще " \
           "1 раза в 3 часа) или автоматические подъемы (актуальную информацию о покупке смотреть в меню покупки\n" \
           "Чтобы купить подъемы, перейдите в списку объявлений, выберите нужно объявление и нажмите \"Купить " \
           "подъемы\". Следуйте инструкциям"
T_HELP_ADMIN = T_HELP + "\n\nЭто было описание, которое видят все пользователи при вводе команды." \
                        "\n\nЧтобы увидеть все команды доступные администратору бота, " \
                        "введите /commands\n\nВсе команды с аргументами можно вводить с разными " \
                        "разделителями. Главное, чтобы перед аргументы был какой-нибудь символ. " \
                        "Например, обе команды \"/add_admin 1\" и \"/add_admin_1\" будут работать. " \
                        "\nuserId - id пользователя в telegram"
T_HELP_VERIFICATION_EDIT = "Чтобы отредактировать заявку, выберите нужное " \
                           "поле (описание, контакты) " \
                           "и нажмите кнопку \"Редактировать\".  " \
                           "Если вы уже отправили заявку, от сперва нужно " \
                           "отменить её (оплата сохранится)"
T_COMMANDS_LIST_D = {
                        "/add_admin": "назначение на роль администратора бота",
                        "/del_admin": "снятие роли администратора бота",
                        "/unverify": "убрать верификацию",
                        "/verify": "верифицировать от лица администратора. Верификация будет записана поверх заявки пользователя",
                        "/user_info": "информация о пользователе",
                        "/ban_user": "заблокировать пользователя",
                        "/unban_user": "разблокировать пользователя",
                        "/user_posts": "публикации пользователя. Формат: [ID пользователя] [Страница]",
                        "/hide_rate": "скрыть тариф покупки автоподъемов",
                        "/create_rate": "создать тариф автоподъемов. Формат: [Время перерыва в секундах] [Цена за 1 штуку]",
                        "/show_rate": "сделать тариф доступным для пользователей",
                        "/set_referral_code": "поставить пользоватлю заданный реферральный код. Фомарт: [ID пользователя] [Код без пробелов]",
                        "/delete_post": "удалить обхявление из БД",
                        "/post_info": "информация о публикации",
                        "/get_rate": "информация о тарифе",
                        "/reset_reports": "сбросить жалобы для данного объявления",
                        "/delete_message": "удалить сообщение по message_id из канала для объявлений",
                        "/copy_table": "выгрузить таблицу с данным названеим из БД в .csv"
                        }

# NOT TO EDIT
URL_CONTACT_ACC = "https://t.me/" + CONTACT_ACC_USERNAME
URL_ACTION = "Пригласите 5 друзей по данной ссылке и " \
             "получите 1 ручной подъем!\nhttps://t.me/" + BOT_USERNAME
URL_ACTION_START_REFERRAL = URL_ACTION + "?start="
URL_ACTION_REPORT = URL_ACTION + "?report_"
CANT_READ_FILE_EXCEPTIONS = FileNotFoundError, FileExistsError, NotADirectoryError
T_COMMANDS_LIST = ""  #  SCROLL BELOW TO GENERATORS
POSSIBLE_COME_TO_SIDEMENU = {1, 4, 100}
POSSIBLE_COME_TO_PAIDSERVICES = {1, 2, 75}
POSSIBLE_COME_TO_CREATEFREELANCEPOST = {2, 4}
POSSIBLE_COME_TO_CATEGORY_FR = {4, 5}
POSSIBLE_COME_TO_CATEGORY_BACK_FR = {4}
POSSIBLE_COME_TO_CATEGORY_CU = {100, 101}
POSSIBLE_COME_TO_CATEGORY_BACK_CU = {100, 101}
POSSIBLE_COME_TO_CREATECUSTOMERPOST = {2}
POSSIBLE_COME_TO_PAYMENTTYPE_FR = {14, 10}
POSSIBLE_COME_TO_PAYMENTTYPE_CU = {105}
POSSIBLE_COME_TO_GUARANTEE_FR = {14}
POSSIBLE_COME_TO_GUARANTEE_CU = {109}
POSSIBLE_COME_TO_SKIP_PORTFOLIO = {8}
POSSIBLE_COME_TO_PORTFOLIO_CU = {103}
POSSIBLE_COME_TO_PREVIEW_POST = {124, 109}
POSSIBLE_COME_TO_POST = {15, 110}
POSSIBLE_COME_TO_PREVIEW_POST_FR = {31, 14}
POSSIBLE_COME_TO_PREVIEW_POST_CU = {124, 109}
POSSIBLE_COME_TO_POST_FR = {15}
POSSIBLE_COME_TO_POST_CU = {110}
POSSIBLE_COME_TO_EDIT_PBP_MENU_FR = {15, 17, 18, 19, 20, 21, 22, 30, 32}
POSSIBLE_COME_TO_EDIT_PBP_MENU_CU = {110, 111, 125, 112, 113, 114, 115, 123}
POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_FR = {31, 32}
POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_CU = {124, 125}
POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_BACK_FR = {32, 31}
POSSIBLE_COME_TO_EDIT_PBP_CATEGORY_BACK_CU = {124, 125}
POSSIBLE_COME_TO_EDIT_PBP_TITLE_FR = {31}
POSSIBLE_COME_TO_EDIT_PBP_TITLE_CU = {124}
POSSIBLE_COME_TO_EDIT_PBP_DESCRIPTION_FR = {31}
POSSIBLE_COME_TO_EDIT_PBP_DESCRIPTION_CU = {124}
POSSIBLE_COME_TO_EDIT_PBP_MEMO = {31}
POSSIBLE_COME_TO_EDIT_PBP_NO_PORTFOLIO_FR = {30, 20}
POSSIBLE_COME_TO_EDIT_PBP_PORTFOLIO_FR = {31, 20}
POSSIBLE_COME_TO_EDIT_PBP_PORTFOLIO_CU = {124, 113}
POSSIBLE_COME_TO_EDIT_CONTACTS_FR = {31}
POSSIBLE_COME_TO_EDIT_CONTACTS_CU = {124}
POSSIBLE_COME_TO_EDIT_PBP_PAYMENT_FR = {31, 23, 27, 28}
POSSIBLE_COME_TO_EDIT_PBP_PAYMENT_CU = {124, 116, 120, 121}
POSSIBLE_COME_TO_EDIT_PBP_PAYMENTTYPE_FR = {22, 23, 24, 25}
POSSIBLE_COME_TO_EDIT_PBP_PAYMENTTYPE_CU = {115, 116, 117, 118}
POSSIBLE_COME_TO_EDIT_PBP_PRICE_FR = {22, 23}
POSSIBLE_COME_TO_EDIT_PBP_PRICE_CU = {116}
POSSIBLE_COME_TO_EDIT_PBP_PRICE_2_FR = {23}
POSSIBLE_COME_TO_EDIT_PBP_PRICE_2_CU = {116}
POSSIBLE_COME_TO_EDIT_PBP_GUARANTEE_FR = {31, 30, 25}
POSSIBLE_COME_TO_EDIT_PBP_GUARANTEE_CU = {124, 123, 118}
POSSIBLE_COME_TO_VERIFICATION_TICKET = {1, 2, 151, 152, 153}
POSSIBLE_COME_TO_BUYING_UPS_MENU = {160, 69, 1, 161, 163, 162}
POSSIBLE_COME_TO_BUYING_AUTO_UPS = {160, 163}
POSSIBLE_COME_TO_BUYING_MANUAL_UPS = {160, 164}
POSSIBLE_COME_TO_RATES_UPS_MENU = {162, 165}

# GENERTATORS
for i in T_COMMANDS_LIST_D.items():
  T_COMMANDS_LIST += i[0] + " - " + i[1] + "\n"
T_COMMANDS_LIST = T_COMMANDS_LIST[:-1]