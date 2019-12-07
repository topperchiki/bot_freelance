# Telegram info
TOKEN = '825727999:AAGTZPK2TRRWZID-rxXicGpFeAbd8dbMyrk'
BOT_USERNAME = "bot_username"
CONTACT_ACC_USERNAME = "google"
ID_POST_CHANNEL = -243828263
USERNAME_POST_CHANNEL = ""
ID_MANAGE_CHANNEL = -243828263
ALLOWED_GROUP_CHATS = {ID_POST_CHANNEL, ID_MANAGE_CHANNEL}
ADMIN_IDS = {}

# Payment
PAYMENT_PROVIDER = '410694247:TEST:1496cc79-d856-44c4-9aa0-0271d717ca9f'

# Files' path
P_ACTIONS = "./data/actions.txt"
P_CATEGORIES = "./data/categories.json"
P_CATEGORIES_R = "./data/categories_r.json"  # relationships
P_D_POSTS = "./data/dposts.json"
P_POSTS = "./data/posts.json"
P_ORDERS = "./data/orders.json"
P_OWNERSHIPS = "./data/ownerships.json"
P_USERS = "./data/users.json"

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
DB_NAME = 'tg_bot_fr'
DB_USER = 'tg_freelance_bot'
DB_HOST = '82.118.21.77'
DB_PASS = '12345'

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

# NOT TO EDIT
URL_CONTACT_ACC = "https://t.me/" + CONTACT_ACC_USERNAME
CANT_READ_FILE_EXCEPTIONS = FileNotFoundError, FileExistsError, NotADirectoryError
POSSIBLE_COME_TO_SIDEMENU = {1, 4, 100}
POSSIBLE_COME_TO_PAIDSERVICES = {1, 75}
POSSIBLE_COME_TO_CREATEFREELANCEPOST = {2, 4}
POSSIBLE_COME_TO_CATEGORY_FR = {4, 5}
POSSIBLE_COME_TO_CATEGORY_BACK_FR = {4}
POSSIBLE_COME_TO_CATEGORY_CU = {100, 101}
POSSIBLE_COME_TO_CATEGORY_BACK_CU = {100, 101}
POSSIBLE_COME_TO_CREATECUSTOMERPOST = {2}
POSSIBLE_COME_TO_PAYMENTTYPE_FR = {14}
POSSIBLE_COME_TO_PAYMENTTYPE_CU = {105}
POSSIBLE_COME_TO_GUARANTEE_FR = {14}
POSSIBLE_COME_TO_GUARANTEE_CU = {109}
POSSIBLE_COME_TO_SKIP_PORTFOLIO = {8}
POSSIBLE_COME_TO_PORTFOLIO_CU = {103}
POSSIBLE_COME_TO_PREVIEW_POST = {124, 109}
POSSIBLE_COME_TO_POST = {15, 110}