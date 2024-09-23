import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram import Router

# Функция для генерации расписания и домашних заданий
def generate_schedule():
    return {
        "schedule": {
            "odd": {  # Расписание для нечетных недель
                "monday": [
                    "Математика(Практика)",
                    "Программирование(Лабораторная)",
                    "Введение в информационные технологии(Лекция)",
                    "Программирование(Лекция)"
                ],
                "tuesday": [
                    "Физкультура",
                    "Философия(Практика)",
                    "Проектная деятельность"
                ],
                "wednesday": [
                    "История(Практика)",
                    "Английский язык",
                    "Физика(Лекция)"
                ],
                "thursday": [
                    "Линейная алгебра(Практика)",
                    "Физика(Практика)",
                    "История(Лекция)"
                ],
                "friday": [
                    "Математика(Лекция)",
                    "Введение в информационные технологии(Лабораторная)"
                ]
            },
            "even": {  # Расписание для четных недель
                "monday": [
                    "Математика(Практика)",
                    "Программирование(Лабораторная)",
                    "Линейная алгебра(Лекция)",
                    "Программирование(Лекция)"
                ],
                "tuesday": [
                    "Физкультура",
                    "Философия(Практика)",
                    "Проектная деятельность"
                ],
                "wednesday": [
                    "История(Практика)",
                    "Английский язык",
                    "Физика(Лекция)"
                ],
                "thursday": [
                    "Физика(Лабораторная)",
                    "Философия(Лекция)",
                    "История(Лекция)"
                ],
                "friday": [
                    "Математика(Лекция)",
                    "Введение в информационные технологии(Лабораторная)"
                ]
            }
        },
        "homework": {str(i): {} for i in range(1, 19)}  # Инициализация домашних заданий для каждой из 18 недель
    }

# Попытка загрузить расписание из файла, если файл не найден - создаем новое расписание
try:
    with open("schedule.json", "r", encoding="utf-8") as f:  # Открываем файл для чтения
        schedule_data = json.load(f)  # Загружаем данные из JSON
except FileNotFoundError:  # Если файл не найден
    schedule_data = generate_schedule()  # Генерируем новое расписание

# Функция для сохранения данных расписания в файл
def save_data():
    with open("schedule.json", "w", encoding="utf-8") as f:  # Открываем файл для записи
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)  # Записываем данные в JSON формате

# Функция для определения четности недели по её номеру
def is_even_week(week_number):
    return week_number % 2 == 0  # Возвращаем True, если номер недели четный

# Токен бота от BotFather
API_TOKEN = ""  # Токен доступа к API Telegram

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)  # Создаем объект бота
dp = Dispatcher()  # Создаем объект диспетчера

# Создаем маршрутизатор для обработки сообщений
router = Router()

# Сопоставление русских дней недели с английскими
days_mapping = {
    "Понедельник": "monday",
    "Вторник": "tuesday",
    "Среда": "wednesday",
    "Четверг": "thursday",
    "Пятница": "friday"
}

# Обратное сопоставление для перевода дней с английского на русский
reverse_days_mapping = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница"
}

# Функция для создания стартовой клавиатуры с основными командами
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Расписание"), KeyboardButton(text="Добавить Д/З")]  # Кнопки для выбора расписания или добавления домашнего задания
        ],
        resize_keyboard=True  # Автоматическое подстраивание клавиатуры под экран устройства
    )
    return keyboard  # Возвращаем созданную клавиатуру

# Функция для создания клавиатуры выбора номера недели
def get_week_number_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(i))] for i in range(1, 19)] + [[KeyboardButton(text="Главное меню")]],  # Кнопки с номерами недель и кнопка для возврата в меню
        resize_keyboard=True  # Автоматическое подстраивание клавиатуры
    )
    return keyboard  # Возвращаем созданную клавиатуру

# Функция для создания клавиатуры выбора дня недели
def get_days_keyboard():
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]  # Список дней недели
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=day)] for day in days] + [[KeyboardButton(text="Главное меню")]],  # Кнопки с днями недели и кнопка для возврата в меню
        resize_keyboard=True  # Автоматическое подстраивание клавиатуры
    )
    return keyboard  # Возвращаем созданную клавиатуру

# Функция для создания клавиатуры выбора урока
def get_lessons_keyboard(week_type, day):
    lessons = schedule_data["schedule"][week_type][day]  # Получаем уроки для указанного типа недели и дня
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"Пара {i + 1}: {lesson}")] for i, lesson in enumerate(lessons)] + [[KeyboardButton(text="Главное меню")]],  # Кнопки с уроками и кнопка для возврата в меню
        resize_keyboard=True  # Автоматическое подстраивание клавиатуры
    )
    return keyboard  # Возвращаем созданную клавиатуру

# Функция для создания клавиатуры выбора типа просмотра расписания
def get_schedule_type_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Посмотреть расписание на день")],  # Кнопка для просмотра расписания на день
            [KeyboardButton(text="Посмотреть расписание на неделю")],  # Кнопка для просмотра расписания на неделю
            [KeyboardButton(text="Добавить Д/З")],  # Кнопка для добавления домашнего задания
            [KeyboardButton(text="Главное меню")]  # Кнопка для возврата в главное меню
        ],
        resize_keyboard=True  # Автоматическое подстраивание клавиатуры
    )
    return keyboard  # Возвращаем созданную клавиатуру

# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply("Привет! Я бот для показа расписания и добавления домашнего задания.", reply_markup=get_main_keyboard())  # Отправляем приветственное сообщение и показываем стартовую клавиатуру

# Глобальные переменные для хранения состояния
state = {
    "week_number": None,  # Хранит номер текущей недели
    "week_type": None  # Хранит тип текущей недели (четная или нечетная)
}

key_ch = ""  # Хранит текущий контекст действия

# Обработчик выбора "Расписание"
@router.message(lambda message: message.text == "Расписание")
async def choose_week_number(message: Message):
    global key_ch  # Используем глобальную переменную для хранения контекста
    key_ch = "rasp"  # Устанавливаем контекст для выбора расписания
    await message.reply("Выберите номер недели (1–18):", reply_markup=get_week_number_keyboard())  # Просим пользователя выбрать номер недели

# Обработчик выбора номера недели для расписания
@router.message(lambda message: message.text.isdigit() and key_ch == "rasp" and 1 <= int(message.text) <= 16)
async def process_week_number_for_schedule(message: Message):
    state["week_number"] = int(message.text)  # Сохраняем выбранный номер недели
    state["week_type"] = "even" if is_even_week(state["week_number"]) else "odd"  # Определяем тип недели

    await message.reply("Выберите, что вы хотите посмотреть:", reply_markup=get_schedule_type_keyboard())  # Запрашиваем тип просмотра расписания

# Обработчик выбора "Посмотреть расписание на день"
@router.message(lambda message: message.text == "Посмотреть расписание на день")
async def choose_day_for_schedule(message: Message):
    await message.reply("Выберите день недели:", reply_markup=get_days_keyboard())  # Предлагаем выбрать день недели для просмотра расписания

# Обработчик выбора дня недели
@router.message(lambda message: message.text in days_mapping.keys() and key_ch == "rasp")
async def process_day_selection(message: Message):
    day = days_mapping[message.text]  # Получаем английский эквивалент дня недели
    week_type = state["week_type"]  # Получаем тип недели

    response = f"Расписание на {message.text} для {state['week_number']}-й недели ({'Четная' if week_type == 'even' else 'Нечетная'}):\n"  # Формируем заголовок сообщения

    lessons = schedule_data["schedule"][week_type][day]  # Получаем уроки для выбранного дня
    for i, lesson in enumerate(lessons, start=1):  # Перебираем уроки
        homework = schedule_data["homework"].get(str(state["week_number"]), {}).get(day, {}).get(str(i), "Домашнего задания нет.")  # Получаем домашнее задание для урока, если оно есть
        response += f"{i}. {lesson} - Д/З: {homework}\n"  # Добавляем информацию об уроке и домашнем задании в ответ

    await message.reply(response, parse_mode=ParseMode.HTML)  # Отправляем пользователю ответ с расписанием

# Обработчик выбора "Посмотреть расписание на неделю"
@router.message(lambda message: message.text == "Посмотреть расписание на неделю")
async def process_week_schedule(message: Message):
    week_type = state["week_type"]  # Получаем тип недели
    week_number = state["week_number"]  # Получаем номер недели

    response = f"Расписание на {week_number}-ю неделю ({'Четная' if week_type == 'even' else 'Нечетная'}):\n"  # Формируем заголовок сообщения

    for day, lessons in schedule_data["schedule"][week_type].items():  # Перебираем дни недели и соответствующие уроки
        day_rus = reverse_days_mapping.get(day, day)  # Получаем русский эквивалент дня
        response += f"\n{day_rus}:\n"  # Добавляем день недели в ответ
        for i, lesson in enumerate(lessons, start=1):  # Перебираем уроки для дня
            homework = schedule_data["homework"].get(str(week_number), {}).get(day, {}).get(str(i), "Домашнего задания нет.")  # Получаем домашнее задание для урока, если оно есть
            response += f"  {i}. {lesson} - Д/З: {homework}\n"  # Добавляем информацию об уроке и домашнем задании в ответ

    await message.reply(response, parse_mode=ParseMode.HTML)  # Отправляем пользователю ответ с расписанием

# Обработка команды "Добавить Д/З"
@router.message(lambda message: message.text == "Добавить Д/З")
async def choose_week_number(message: Message):
    global key_ch  # Используем глобальную переменную для хранения контекста
    key_ch = "dz"  # Устанавливаем контекст для добавления домашнего задания
    await message.reply("Выберите номер недели (1–16):", reply_markup=get_week_number_keyboard())  # Просим пользователя выбрать номер недели для домашнего задания

# Храним состояние для домашнего задания
add_homework_state = {
    "week_number": None,  # Номер недели для домашнего задания
    "week_type": None,  # Тип недели (четная или нечетная)
    "day": None,  # День недели для домашнего задания
    "lesson_number": None  # Номер урока для домашнего задания
}

# Обработчик выбора номера недели для домашнего задания
@router.message(lambda message: message.text.isdigit() and key_ch == "dz" and 1 <= int(message.text) <= 16)
async def process_week_number_for_homework(message: Message):
    add_homework_state["week_number"] = int(message.text)  # Сохраняем выбранный номер недели
    add_homework_state["week_type"] = "even" if is_even_week(add_homework_state["week_number"]) else "odd"  # Определяем тип недели

    await message.reply("Выберите день недели:", reply_markup=get_days_keyboard())  # Запрашиваем день недели для добавления домашнего задания

# Обработчик выбора дня недели для домашнего задания
@router.message(lambda message: message.text in days_mapping.keys() and key_ch == "dz")
async def process_day_for_homework(message: Message):
    add_homework_state["day"] = days_mapping[message.text]  # Сохраняем английский эквивалент дня недели

    await message.reply("Выберите урок:", reply_markup=get_lessons_keyboard(add_homework_state["week_type"], add_homework_state["day"]))  # Запрашиваем урок для добавления домашнего задания

# Обработчик выбора урока для домашнего задания
@router.message(lambda message: "Пара" in message.text and key_ch == "dz")
async def process_lesson_selection(message: Message):
    add_homework_state["lesson_number"] = int(message.text.split()[1][0])  # Сохраняем номер урока, извлекая его из текста сообщения

    await message.reply(f"Напишите домашнее задание для {message.text}:", reply_markup=get_main_keyboard())  # Запрашиваем текст домашнего задания

# Обработчик отправки домашнего задания
@router.message(lambda message: key_ch == "dz" and add_homework_state["lesson_number"] is not None)
async def save_homework(message: Message):
    week_number = add_homework_state["week_number"]  # Получаем номер недели
    day = add_homework_state["day"]  # Получаем день недели
    lesson_number = add_homework_state["lesson_number"]  # Получаем номер урока

    # Сохраняем домашнее задание в структуру данных расписания
    schedule_data["homework"].setdefault(str(week_number), {}).setdefault(day, {})[str(lesson_number)] = message.text
    save_data()  # Сохраняем изменения в файле

    await message.reply("Домашнее задание добавлено!", reply_markup=get_main_keyboard())  # Сообщаем пользователю об успешном добавлении
    key_ch = ""  # Сбрасываем состояние после добавления

# Обработка команды "Главное меню"
@router.message(lambda message: message.text == "Главное меню")
async def go_to_main_menu(message: Message):
    await message.reply("Вы вернулись в главное меню.", reply_markup=get_main_keyboard())  # Сообщаем о возвращении в главное меню

# Запуск бота
async def main():
    dp.include_router(router)  # Подключаем маршрутизатор к диспетчеру
    await dp.start_polling(bot)  # Запускаем опрос сообщений от пользователей

# Точка входа в программу
if __name__ == "__main__":
    asyncio.run(main())