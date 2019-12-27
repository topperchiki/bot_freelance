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

# Files' path
P_ACTIONS = "./data/actions.txt"

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
DB_USER = 'testrole'
DB_HOST = '127.0.0.1'
DB_PASS = '123456'

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
T_HELP_ADMIN = ""
T_COMMANDS_LIST_D = {"/add_admin_АйдиЮзера": "назначение на роль администратора бота",
                        "/del_admin_АйдиЮзера": "снятие роли администратора бота",
                        "/unverify": "",
                        "/verify": "",
                        "/user_info": "",
                        "/ban_user": "",
                        "/delete_user": "",
                        "/user_posts": "",
                        "/hide_rate": "",
                        "/delete_rate": "",
                        "/create_rate": "",
                        "/show_rate": "",
                        "/set_referral_code": "",
                        "/list_posts": "",
                        "/delete_post": "",
                        "/post_info": "",
                        "/clear_cache": ""
                        }

# NOT TO EDIT
URL_CONTACT_ACC = "https://t.me/" + CONTACT_ACC_USERNAME
CANT_READ_FILE_EXCEPTIONS = FileNotFoundError, FileExistsError, NotADirectoryError
T_COMMANDS_LIST = ""  #  SCROLL BELOW TO GENERATORS
POSSIBLE_COME_TO_SIDEMENU = {1, 4, 100}
POSSIBLE_COME_TO_PAIDSERVICES = {1, 75}
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

# GENERTATORS
for i in T_COMMANDS_LIST.items():
  T_COMMANDS_LIST += i[0] + " - " + i[1] + "\n"
T_COMMANDS_LIST = T_COMMANDS_LIST[:-1]