import configparser
import telebot

mainConfig = configparser.ConfigParser()
mainConfig.read(f'config.ini',encoding='utf-8-sig')

#Получение otrs секции конфигурации
OTRS_USERNAME = mainConfig.get("OTRS", "username")
OTRS_PASSWORD = mainConfig.get("OTRS", "password")
OTRS_QUEUE = mainConfig.get("OTRS", "queue")


#Получение Telegram сессии конфигурации
TBot = telebot.TeleBot(str(mainConfig.get("Telegram", "token")),parse_mode='HTML', threaded=True, num_threads=2)
TBot_chat_id = mainConfig.get("Telegram", "chat_id")

COOKIE_FILENAME = mainConfig.get("Other", "cookie_filename")

#База для сбора тикетов
DB_NAME = mainConfig.get("Database","tickets_filename")
import sqlite3
TICKETS_DB_CONNECTION = sqlite3.connect(DB_NAME, check_same_thread=False)
TICKETS_DB_CURSOR = TICKETS_DB_CONNECTION.cursor()
TICKETS_DB_CURSOR.execute('''CREATE TABLE IF NOT EXISTS Tickets (Number INTEGER,Link TEXT);''')
TICKETS_DB_CONNECTION.commit()

import threading
DB_LOCKER = threading.Lock()


#Таймаут проверки
CHECK_TIMEOUT = int(mainConfig.get("Other", "check_timeout"))