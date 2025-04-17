import asyncio
import sqlite3
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, PreCheckoutQuery, LabeledPrice
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, CommandStart

API_TOKEN = "7439367536:AAFBhTl3XqRusC5RQejU6B65r5gmtTpuCJ0"
PAYMENT_PROVIDER_TOKEN = "6618536796:TEST:545158"
ADMIN_USER_ID = 650963487

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Доступные языки и переводы
LANGUAGES = {
    "kg": "Кыргызча",
    "ru": "Русский",
    "en": "English"
}

TRANSLATIONS = {
    "choose_language": {
        "kg": "Тилди тандаңыз:",
        "ru": "Выберите язык:",
        "en": "Please choose a language:"
    },
    "welcome_message": {
        "kg": "Саламатсызбы! Биздин туризм ботубузга кош келиңиз.",
        "ru": "Здравствуйте! Добро пожаловать в нашего туристического бота.",
        "en": "Hello! Welcome to our tourism bot."
    },
    "main_menu": {
        "kg": "Башкы меню:",
        "ru": "Главное меню:",
        "en": "Main menu:"
    },
    "view_tours": {
        "kg": "Турларды көрүү",
        "ru": "Посмотреть туры",
        "en": "View Tours"
    },
    "book_tour": {
        "kg": "Турга жазылуу",
        "ru": "Забронировать тур",
        "en": "Book a Tour"
    },
    "contact_us": {
        "kg": "Биз менен байланышыңыз",
        "ru": "Связаться с нами",
        "en": "Contact Us"
    },
    "faq": {
        "kg": "FAQ суроолору",
        "ru": "Часто задаваемые вопросы",
        "en": "FAQ"
    },
    "send_message": {
        "kg": "Бизге билдирүү жибериңиз, биздин операторлор жакында жооп беришет.",
        "ru": "Пожалуйста, отправьте нам сообщение, и наши операторы скоро ответят.",
        "en": "Please send us your message and our operators will respond shortly."
    },
    "faq_text": {
        "kg": "FAQ:\n\nС: Турга кантип жазылсам болот?\nЖ: 'Турга жазылуу' дегенди тандап турга жазылсаңыз болот.\n\nС: Колдоо кызматына кантип кайрылсам болот?\nЖ: 'Биз менен байланышыңыз' дегенди тандап колдоо кызматына кайрылсаңыз болот.",
        "ru": "FAQ:\n\nВ: Как забронировать тур?\nО: Вы можете забронировать тур, выбрав опцию 'Забронировать тур'.\n\nВ: Как связаться с поддержкой?\nО: Вы можете связаться с поддержкой, выбрав опцию 'Связаться с нами'.",
        "en": "FAQ:\n\nQ: How to book a tour?\nA: You can book a tour by selecting the 'Book a Tour' option.\n\nQ: How to contact support?\nA: You can contact support by selecting the 'Contact Us' option."
    },
    "message_received": {
        "kg": "Сиздин билдирүүңүз кабыл алынды. Биз жакында сиз менен байланышабыз.",
        "ru": "Ваше сообщение получено. Мы свяжемся с вами в ближайшее время.",
        "en": "Your message has been received. We will contact you shortly."
    },
    "select_date": {
        "kg": "Турдун датасын тандаңыз:",
        "ru": "Выберите дату тура:",
        "en": "Please select tour date:"
    },
    "invalid_people_input": {
        "kg": "Сураныч, туура адамдар санын киргизиңиз (0 дон чоң сан):",
        "ru": "Пожалуйста, введите корректное количество людей (число больше 0):",
        "en": "Please enter a valid number of people (greater than 0):"
    },
    "invalid_date_format": {
        "kg": "Сураныч, датаны туура формаатта киргизиңиз (YYYY-MM-DD):",
        "ru": "Пожалуйста, введите дату в правильном формате (YYYY-MM-DD):",
        "en": "Please enter the date in correct format (YYYY-MM-DD):"
    },
    "select_tour": {
        "kg": "Турду тандаңыз:",
        "ru": "Выберите тур:",
        "en": "Please select a tour:"
    },
    "select_date": {
        "kg": "Турдун датасын тандаңыз:",
        "ru": "Выберите дату тура:",
        "en": "Please select tour date:"
    },
    "invalid_people_input": {
        "kg": "Сураныч, туура адамдар санын киргизиңиз (0 дон чоң сан):",
        "ru": "Пожалуйста, введите корректное количество людей (число больше 0):",
        "en": "Please enter a valid number of people (greater than 0):"
    },
    "enter_people": {
        "kg": "Канча адам барарын жазыңыз:",
        "ru": "Введите количество людей:",
        "en": "Enter the number of people:"
    },
    "enter_date": {
        "kg": "Турдун датасын тандаңыз:",
        "ru": "Выберите дату тура:",
        "en": "Select tour date:"
    },
    "enter_phone": {
        "kg": "Байланыш номерин жазыңыз:",
        "ru": "Введите ваш номер телефона:",
        "en": "Enter your phone number:"
    },
    "enter_name": {
        "kg": "Сиздин атыңызды жазыңыз:",
        "ru": "Введите ваше имя:",
        "en": "Enter your name:"
    },
    "enter_comment": {
        "kg": "Комментарий (милдеттүү эмес):",
        "ru": "Введите комментарий (необязательно):",
        "en": "Enter a comment (optional):"
    },
    "confirmation_prompt": {
        "kg": "Маалымат туурабы?\n{details}\nТуура болсо, 'Ооба' баскычын басыңыз.",
        "ru": "Информация верна?\n{details}\nЕсли верно, нажмите кнопку 'Да'.",
        "en": "Is the information correct?\n{details}\nIf correct, press the 'Yes' button."
    },
    "payment_prompt": {
        "kg": "Сиздин бонустук төлөмүңүз 20% түзөт. Төлөөгө киришиңиз.",
        "ru": "Ваш авансовый платеж составляет 20%. Перейдите к оплате.",
        "en": "Your advance payment is 20%. Proceed to payment."
    },
    "booking_success": {
        "kg": "Тур ийгиликтүү брондолду! Биз жакында сиз менен байланышабыз.",
        "ru": "Тур успешно забронирован! Мы свяжемся с вами в ближайшее время.",
        "en": "The tour has been successfully booked! We will contact you shortly."
    },
    "admin_notification": {
        "kg": "Жаңы брондоо:\nТур: {tour_name}\nАдамдар саны: {people}\nДата: {date}\nТелефон: {phone}\nБрондолгон адам: {name}\nКомментарий: {comment}",
        "ru": "Новое бронирование:\nТур: {tour_name}\nКоличество людей: {people}\nДата: {date}\nТелефон: {phone}\nБронирующий: {name}\nКомментарий: {comment}",
        "en": "New booking:\nTour: {tour_name}\nNumber of people: {people}\nDate: {date}\nPhone: {phone}\nBooker: {name}\nComment: {comment}"
    }

}

# # Данные о доступных турах
# TOURS = [
#     {"id": 1, "name": {"kg": "Ысык-Көл", "ru": "Иссык-Куль", "en": "Issyk-Kul"}, "price_per_person": 100},
#     {"id": 2, "name": {"kg": "Ала-Арча", "ru": "Ала-Арча", "en": "Ala-Archa"}, "price_per_person": 50},
#     {"id": 3, "name": {"kg": "Сары-Челек", "ru": "Сары-Челек", "en": "Sary-Chelek"}, "price_per_person": 120}
# ]


# Добавляем новые состояния для админ-панели
class AdminState(StatesGroup):
    managing_tours = State()
    adding_tour = State()
    waiting_for_name_kg = State()
    waiting_for_name_ru = State()
    waiting_for_name_en = State()
    waiting_for_price = State()
    deleting_tour = State()
    waiting_for_dates = State()


# FSM для процесса бронирования
class BookingState(StatesGroup):
    waiting_for_people = State()
    waiting_for_date = State()
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_comment = State()

# База данных
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    
    # Создаем таблицу tours, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_kg TEXT NOT NULL,
            name_ru TEXT NOT NULL,
            name_en TEXT NOT NULL,
            price_per_person INTEGER NOT NULL,
            dates TEXT NOT NULL
        )
    ''')
    
    # Создаем остальные таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'en'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            admin_reply TEXT,
            reply_timestamp DATETIME,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Функции для управления языком пользователя
def get_user_language(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "en"

def set_user_language(user_id, language):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    conn.close()

def get_translation(user_id, key):
    language = get_user_language(user_id)
    return TRANSLATIONS.get(key, {}).get(language, TRANSLATIONS[key]["en"])

async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"set_lang:{code}")]
            for code, name in LANGUAGES.items()
        ]
    )
    await message.answer(get_translation(message.from_user.id, "choose_language"), reply_markup=keyboard)

async def language_callback_handler(callback_query: CallbackQuery):
    action, code = callback_query.data.split(":")
    user_id = callback_query.from_user.id
    if action == "set_lang" and code in LANGUAGES:
        # Удаляем сообщение с выбором языка
        await callback_query.message.delete()
        
        set_user_language(user_id, code)
        await callback_query.message.answer(get_translation(user_id, "welcome_message"))
        await show_main_menu(callback_query.message, user_id)
    await callback_query.answer()



async def show_main_menu(message_or_callback, user_id: int):
    """Отображает главное меню (не удаляет предыдущие сообщения)."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_translation(user_id, "view_tours"), url="https://wordtravel.local/")],
        [InlineKeyboardButton(text=get_translation(user_id, "book_tour"), callback_data="book_tour")],
        [InlineKeyboardButton(text=get_translation(user_id, "contact_us"), callback_data="contact_us")],
        [InlineKeyboardButton(text=get_translation(user_id, "faq"), callback_data="faq")]
    ])
    
    if isinstance(message_or_callback, types.Message):
        # Для нового сообщения просто отправляем меню
        await message_or_callback.answer(get_translation(user_id, "main_menu"), reply_markup=keyboard)
    elif isinstance(message_or_callback, CallbackQuery):
        # Для callback обновляем существующее сообщение
        try:
            await message_or_callback.message.edit_text(
                get_translation(user_id, "main_menu"), 
                reply_markup=keyboard
            )
        except:
            # Если сообщение уже было изменено, отправляем новое
            await message_or_callback.message.answer(
                get_translation(user_id, "main_menu"), 
                reply_markup=keyboard
            )




# Добавляем функции для работы с турами
def get_all_tours():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tours")
    tours = cursor.fetchall()
    conn.close()
    return tours

def add_tour(name_kg, name_ru, name_en, price, dates):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tours (name_kg, name_ru, name_en, price_per_person, dates)
        VALUES (?, ?, ?, ?, ?)
    ''', (name_kg, name_ru, name_en, price, dates))
    conn.commit()
    conn.close()

def delete_tour(tour_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tours WHERE id = ?", (tour_id,))
    conn.commit()
    conn.close()

# Обработчики админ-панели
async def admin_command(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Управление турами", callback_data="manage_tours")],
            [InlineKeyboardButton(text="Просмотр сообщений", callback_data="view_messages")]
        ])
        await message.answer("Админ-панель:", reply_markup=keyboard)

async def handle_admin_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == "manage_tours":
        await manage_tours(callback.message)
    elif callback.data == "view_messages":
        await show_unanswered_messages(callback.message)
    await callback.answer()

async def manage_tours(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить тур", callback_data="add_tour")],
        [InlineKeyboardButton(text="Удалить тур", callback_data="delete_tour")],
        [InlineKeyboardButton(text="Назад", callback_data="admin_back")]
    ])
    await message.answer("Управление турами:", reply_markup=keyboard)

async def handle_tour_management(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_tour":
        await callback.message.answer("Введите название тура на кыргызском:")
        await state.set_state(AdminState.waiting_for_name_kg)
    elif callback.data == "delete_tour":
        tours = get_all_tours()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{t[1]} ({t[4]} USD)", callback_data=f"delete_tour:{t[0]}")]
            for t in tours
        ])
        await callback.message.answer("Выберите тур для удаления:", reply_markup=keyboard)
    await callback.answer()

# FSM обработчики для добавления тура
async def process_name_kg(message: types.Message, state: FSMContext):
    await state.update_data(name_kg=message.text)
    await message.answer("Введите название тура на русском:")
    await state.set_state(AdminState.waiting_for_name_ru)

async def process_name_ru(message: types.Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    await message.answer("Введите название тура на английском:")
    await state.set_state(AdminState.waiting_for_name_en)

async def process_name_en(message: types.Message, state: FSMContext):
    await state.update_data(name_en=message.text)
    await message.answer("Введите цену за человека (USD):")
    await state.set_state(AdminState.waiting_for_price)

async def process_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError
            
        await state.update_data(price=price)
        await message.answer("Введите даты через запятую (формат YYYY-MM-DD):")
        await state.set_state(AdminState.waiting_for_dates)
        
    except ValueError:
        await message.answer("❌ Цена должна быть целым числом больше 0!")

# Новый обработчик для ввода дат
async def process_dates(message: types.Message, state: FSMContext):
    try:
        dates = [datetime.strptime(d.strip(), "%Y-%m-%d").strftime("%Y-%m-%d") 
                for d in message.text.split(",")]
        
        data = await state.get_data()
        add_tour(
            data['name_kg'],
            data['name_ru'],
            data['name_en'],
            data['price'],
            ",".join(dates)
        )
        
        await message.answer(f"✅ Тур добавлен!\nЦена: {data['price']} $\nДаты: {', '.join(dates)}")
        await state.clear()
        
    except ValueError as e:
        await message.answer(f"❌ Ошибка формата даты: {e}\nПример: 2024-01-01,2024-01-15")


# Обработчик удаления тура
async def delete_tour_handler(callback: CallbackQuery):
    tour_id = int(callback.data.split(":")[1])
    delete_tour(tour_id)
    await callback.message.answer("Тур успешно удален!")
    await callback.answer()

# Просмотр сообщений
async def show_unanswered_messages(message: types.Message):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE admin_reply IS NULL")
    messages = cursor.fetchall()
    conn.close()
    
    if not messages:
        await message.answer("Нет новых сообщений")
        return
    
    for msg in messages:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data=f"reply:{msg[0]}")]
        ])
        await message.answer(
            f"Сообщение от пользователя {msg[1]}:\n\n{msg[2]}\n\n"
            f"Время: {msg[5]}",
            reply_markup=keyboard
        )




# FSM для процесса "Связаться с нами"
class ContactState(StatesGroup):
    waiting_for_message = State()

# Добавляем новое состояние для ответа администратора
class AdminReplyState(StatesGroup):
    waiting_for_reply = State()

# Модифицированный обработчик "Связаться с нами"
async def contact_us_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    try:
        await callback_query.message.delete()
    except:
        pass
    await callback_query.message.answer(get_translation(user_id, "send_message"))
    await state.set_state(ContactState.waiting_for_message)
    await callback_query.answer()

async def process_contact_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Сохраняем сообщение в БД
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (user_id, message) 
        VALUES (?, ?)
    """, (user_id, message.text))
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Отправляем админу сообщение с кнопкой ответа
    admin_msg = await message.bot.send_message(
        ADMIN_USER_ID,
        f"✉️ Новое сообщение от {message.from_user.full_name} (ID: {user_id}):\n\n{message.text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Ответить", 
                callback_data=f"reply:{user_id}:{message_id}"
            )]
        ])
    )

    await message.answer(get_translation(user_id, "message_received"))
    await show_main_menu(message, user_id)
    await state.clear()

# Новый обработчик кнопки "Ответить"
async def handle_admin_reply(callback: CallbackQuery, state: FSMContext):
    _, user_id, message_id = callback.data.split(":")
    await state.update_data(
        target_user=int(user_id),
        message_id=int(message_id)
    )
    await callback.message.answer("Введите ваш ответ пользователю:")
    await state.set_state(AdminReplyState.waiting_for_reply)
    await callback.answer()

# Обработчик ответа администратора
async def process_admin_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_user = data['target_user']
    message_id = data['message_id']
    reply_text = message.text

    # Сохраняем ответ в БД
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE messages 
        SET admin_reply = ?, reply_timestamp = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (reply_text, message_id))
    conn.commit()
    conn.close()

    # Отправляем ответ пользователю
    await bot.send_message(
        chat_id=target_user,
        text=f"📩 Ответ от поддержки:\n\n{reply_text}"
    )

    # Уведомление администратору
    await message.answer("✅ Ответ успешно отправлен!")
    await state.clear()


async def faq_callback_handler(callback_query: CallbackQuery):
    """Обработчик для кнопки FAQ."""
    user_id = callback_query.from_user.id
    # Отправляем FAQ как новое сообщение (не удаляем меню)
    await callback_query.message.answer(get_translation(user_id, "faq_text"))
    await callback_query.answer()

# Обработчик кнопки "Бронирование тура" (начало процесса выбора тура)
async def book_tour_callback_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    tours = get_all_tours()
    language = get_user_language(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=tour[1 if language == 'kg' else 2 if language == 'ru' else 3],
            callback_data=f"tour:{tour[0]}"
        )] for tour in tours
    ])
    
    await callback_query.message.answer(
        get_translation(user_id, "select_tour"),
        reply_markup=keyboard
    )
    await callback_query.answer()

# Обработчик выбора тура
async def tour_selected_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    try:
        tour_id = int(callback_query.data.split(":")[1])
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tours WHERE id = ?", (tour_id,))
        tour = cursor.fetchone()
        conn.close()
        
        if not tour:
            raise ValueError("Tour not found")
            
        price = int(tour[4])  # Гарантированно integer после исправлений
        dates = tour[5].split(",")
        
        await state.update_data(tour={
            "id": tour[0],
            "name": {"kg": tour[1], "ru": tour[2], "en": tour[3]},
            "price_per_person": price,
            "dates": dates
        })
        
        # Показываем клавиатуру с датами
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=date, callback_data=f"tour_date:{date}")]
            for date in dates
        ])
        
        await callback_query.message.answer(
            get_translation(callback_query.from_user.id, "select_date"),
            reply_markup=keyboard
        )
        await state.set_state(BookingState.waiting_for_date)
        
    except Exception as e:
        logger.error(f"Tour selection error: {e}")
        await callback_query.answer("⚠️ Ошибка выбора тура")

    await callback_query.answer()


# FSM: Обработка количества людей
async def process_people(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        people = int(message.text)
        if people <= 0:
            raise ValueError
        await state.update_data(people=people)
        
        # Получаем перевод для следующего шага
        text = get_translation(user_id, "enter_phone")
        await message.answer(text)
        await state.set_state(BookingState.waiting_for_phone)
        
    except ValueError:
        # Используем перевод для сообщения об ошибке
        error_text = get_translation(user_id, "invalid_people_input")
        await message.answer(error_text)

# FSM: Обработка даты тура
async def date_selected_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    selected_date = callback_query.data.split(":")[1]
    await state.update_data(date=selected_date)
    
    # Получаем перевод для текущего языка пользователя
    text = get_translation(user_id, "enter_people")
    await callback_query.message.answer(text)
    await state.set_state(BookingState.waiting_for_people)
    await callback_query.answer()


# FSM: Обработка номера телефона
async def process_phone(message: types.Message, state: FSMContext):
    """Обрабатывает ввод номера телефона."""
    await state.update_data(phone=message.text)
    await state.set_state(BookingState.waiting_for_name)
    await message.answer(get_translation(message.from_user.id, "enter_name"))

# FSM: Обработка имени
async def process_name(message: types.Message, state: FSMContext):
    """Обрабатывает ввод имени."""
    await state.update_data(name=message.text)
    await state.set_state(BookingState.waiting_for_comment)
    await message.answer(get_translation(message.from_user.id, "enter_comment"))

# FSM: Обработка комментария и подтверждение бронирования
async def process_comment(message: types.Message, state: FSMContext):
    """Обрабатывает ввод комментария и подтверждает данные."""
    await state.update_data(comment=message.text)

    # Получаем все данные из состояния FSM
    data = await state.get_data()
    details = (
        f"Тур: {data['tour']['name'][get_user_language(message.from_user.id)]}\n"
        f"Количество людей: {data['people']}\n"
        f"Дата: {data['date']}\n"
        f"Телефон: {data['phone']}\n"
        f"Имя: {data['name']}\n"
        f"Комментарий: {data['comment'] or 'Нет'}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="Нет", callback_data="cancel_booking")]
    ])
    await message.answer(get_translation(message.from_user.id, "confirmation_prompt").format(details=details), reply_markup=keyboard)

async def cancel_booking_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик отмены бронирования."""
    await state.clear()
    user_id = callback_query.from_user.id
    await callback_query.message.answer("Бронирование отменено.")
    await show_main_menu(callback_query, user_id)
    await callback_query.answer()

    
# Обработчик подтверждения бронирования
async def confirm_booking_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Исправляем преобразование данных
    try:
        price = int(data["tour"]["price_per_person"])
        people = int(data["people"])
        total_price = price * people
        advance_payment = int(total_price * 0.2)
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error calculating price: {e}")
        await callback_query.answer("Произошла ошибка в расчетах")
        return

    # Остальная часть кода без изменений
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title="Tour Booking",
        description=f"{data['tour']['name'][get_user_language(callback_query.from_user.id)]} (20% предоплата)",
        payload=str(callback_query.from_user.id),
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="USD",
        prices=[LabeledPrice(label="Предоплата", amount=advance_payment * 100)]
    )
    await callback_query.answer()

# Обработчик предоплаты
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Обрабатывает предоплату."""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработчик успешной оплаты
async def successful_payment_handler(message: types.Message, state: FSMContext):
    """Обрабатывает успешную оплату."""
    user_id = int(message.successful_payment.invoice_payload)
    data = await state.get_data()  # Получаем данные из состояния
    
    # Отправляем подтверждение
    await bot.send_message(user_id, get_translation(user_id, "booking_success"))
    
    # Отправляем уведомление админу
    admin_message = get_translation(user_id, "admin_notification").format(
        tour_name=data['tour']['name'][get_user_language(user_id)],
        people=data['people'],
        date=data['date'],
        phone=data['phone'],
        name=data['name'],
        comment=data.get('comment', 'Нет')
    )
    await bot.send_message(ADMIN_USER_ID, admin_message)
    
    await state.clear()

async def main():
    """Главная функция запуска бота."""
    init_db()
    global bot, dp
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация обработчиков с правильным порядком
    dp.message.register(start_handler, CommandStart())
    dp.message.register(admin_command, Command("admin"))
    # Сначала регистрируем обработчики FSM состояний
    dp.message.register(process_people, BookingState.waiting_for_people)
    dp.message.register(process_phone, BookingState.waiting_for_phone)
    dp.message.register(process_name, BookingState.waiting_for_name)
    dp.message.register(process_comment, BookingState.waiting_for_comment)
    dp.message.register(process_contact_message, ContactState.waiting_for_message)

    dp.message.register(process_name_kg, AdminState.waiting_for_name_kg)
    dp.message.register(process_name_ru, AdminState.waiting_for_name_ru)
    dp.message.register(process_name_en, AdminState.waiting_for_name_en)
    dp.message.register(process_price, AdminState.waiting_for_price)

    # Общие обработчики сообщений
    dp.message.register(successful_payment_handler, lambda message: message.successful_payment is not None)

    # Регистрация callback-обработчиков
    dp.callback_query.register(language_callback_handler, lambda c: c.data.startswith("set_lang:"))
    dp.callback_query.register(faq_callback_handler, lambda c: c.data == "faq")
    dp.callback_query.register(contact_us_callback_handler, lambda c: c.data == "contact_us")
    dp.callback_query.register(book_tour_callback_handler, lambda c: c.data == "book_tour")
    dp.callback_query.register(tour_selected_callback_handler, lambda c: c.data.startswith("tour:"))
    dp.callback_query.register(confirm_booking_handler, lambda c: c.data == "confirm_booking")
    dp.pre_checkout_query.register(pre_checkout_handler)
    dp.callback_query.register(cancel_booking_handler, lambda c: c.data == "cancel_booking")
    dp.callback_query.register(handle_admin_reply, lambda c: c.data.startswith("reply:"))
    dp.message.register(process_admin_reply, AdminReplyState.waiting_for_reply)

    dp.callback_query.register(handle_admin_callback, lambda c: c.data in ["manage_tours", "view_messages"])
    dp.callback_query.register(handle_tour_management, lambda c: c.data in ["add_tour", "delete_tour"])
    dp.callback_query.register(delete_tour_handler, lambda c: c.data.startswith("delete_tour:"))

    dp.message.register(process_dates, AdminState.waiting_for_dates)
    dp.callback_query.register(date_selected_callback_handler, lambda c: c.data.startswith("tour_date:"))

    await dp.start_polling(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())