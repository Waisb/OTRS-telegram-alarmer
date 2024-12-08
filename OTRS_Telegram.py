from globals import OTRS_QUEUE, TBot_chat_id, TBot, COOKIE_FILENAME, CHECK_TIMEOUT
from otrs import OTRS
import time
from telebot import types
from logger import Log

# Создаём сессию
session = OTRS()
#Грузим куки с файла
if session.load_cookie(session, COOKIE_FILENAME) == False: Log.info("Куки не загружены")
else: Log.info("Куки загружены")
#Проверяем сессию
if session.validate_session(session) == False:
    Log.warning("Сессия не актуальна")
    session.update_session(session)
else:
    Log.info("Сессия в норме")

#Проверка старта телеграмма.
try:
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Страница проекта👀", url="https://github.com/Waisb/OTRS-telegram-alarmer"))
    TBot.send_message(TBot_chat_id, "Бот был запущен✅", reply_markup=keyboard)
    Log.info("Бот был запущен")
except Exception as EXCEPTION:
    Log.critical(str(EXCEPTION))
    exit()

#Цикл проверки (основной цикл)
while True:
    try:
        Log.info("Проверка очереди")
        tickets = session.get_tickets(OTRS_QUEUE)
        #Ошибка при получении тикетов 
        if tickets == False:
            Log.warning("Сессия стала неактуальна или получение тикетов произошло с ошибкой. Требуется обновление")
            session.update_session(session)
            continue
        #Тикеты есть
        for ticket in tickets:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Перейти к тикету ->", url=ticket["Link"]))
            TBot.send_message(TBot_chat_id, f"Новый тикет!\n\nНомер: {ticket["Number"]}\nТема: {ticket["Title"]}\n\nОтправитель: {ticket["Sender"]}\nКлиент: {ticket["Client"]}",reply_markup=keyboard)
        
        Log.info(f"Переход в таймаут: {CHECK_TIMEOUT} секунд")
        time.sleep(CHECK_TIMEOUT)
    #Для исключений по типу обрыва соединения.
    except Exception as EXCEPTION:
        Log.critical(str(EXCEPTION))
        Log.info(f"Переход в таймаут: {CHECK_TIMEOUT} секунд")
        time.sleep(CHECK_TIMEOUT)
        continue
