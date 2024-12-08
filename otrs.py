from globals import OTRS_QUEUE, COOKIE_FILENAME, OTRS_USERNAME, OTRS_PASSWORD,CHECK_TIMEOUT
import json
import requests
import os.path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from collector import ticket_exist, ticket_add
from logger import Log


class OTRS:
    def __init__(self):
        self.session = requests.Session()
    
    def validate_session(self, session):
        '''
        Проверка страницы на наличие окна логина. 
        Возвращает false если окно входа найдено. Т.е сессия не актуальна.
        Возвращает true если окно входа не найдено. Т.е пустило в систему.
        '''
        response = self.session.get(OTRS_QUEUE)
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find('body')
        if len(body.attrs['class']) > 0:
            if body.attrs['class'][0] == 'LoginScreen':
                Log.warning("Обнаружена страница входа, сессия устарела")
                return False
        else:
            Log.warning("Страница входа не обнаружена, предполагается что сессия в норме.")
            return True

    def load_cookie(self, session, cookie_filename):
        try: 
            # Читаем cookies из файла
            if os.path.exists(cookie_filename):
                if os.stat(cookie_filename).st_size == 0: #Файл пуст, его не пустит json.load()
                    os.remove(cookie_filename) #Удаление файла.
                    return False
                else:
                    with open(cookie_filename, 'r') as file:
                        cookies = json.load(file)
                    # Устанавливаем cookies в сессию
                    for cookie in cookies:
                        self.session.cookies.set(name=cookie['name'], value=cookie['value'], domain=cookie['domain'], path=cookie['path'])
                    return True
            else:
                Log.warning("Не найден файл с куки. Создание...")
                with open(cookie_filename, "w") as file:
                    file.close()
                return False

        except Exception as EXCEPTION:
            Log.critical(f"{str(EXCEPTION)}")
            return False

    def update_session(self, session, update_cookie = True):
        #TODO: Ссылку тут надо будет разбивать и получать домен. Чтобы код подтягивал любые данные с конфига. 
        #TODO: При передаче юзернейма и пароля, нужно переводить спецсимволы в html вид. (слеши например)
        from urllib.parse import urlparse
        parsed_url = urlparse(OTRS_QUEUE)
        self.session.get(f"{parsed_url.scheme}://{parsed_url.netloc}/otrs/index.pl?Action=Login&RequestedURL=Action%3DAgentTicketQueue&Lang=ru&TimeZoneOffset=-180&User={OTRS_USERNAME}&Password={OTRS_PASSWORD}")
        if self.validate_session(session): #Сессия обновлена, выполнен вход
            Log.warning("Сессия обновлена!")
            if update_cookie: #Обновление кук в файле если требуется.
                cookies = self.session.cookies
                cookies_list = []
                for cookie in cookies:
                    cookies_list.append({
                        "domain": cookie.domain,
                        "httpOnly": bool(cookie.has_nonstandard_attr('httponly')),
                        "name": cookie.name,
                        "path": cookie.path,
                        "sameSite": cookie._rest.get('samesite'),
                        "secure": cookie.secure,
                        "value": cookie.value
                    })
                with open(COOKIE_FILENAME, 'w', encoding='utf-8') as f:
                    json.dump(cookies_list, f, ensure_ascii=False, indent=4)
                Log.warning(f"Куки сохранены в {COOKIE_FILENAME}")
                return True
        else: #Произошла ошибка
            Log.warning(f"Ошибка входа!")
            return False
    
    def get_tickets(self, queue):
        try: 
            queue_page = self.session.get(queue)
            soup = BeautifulSoup(queue_page.text, "lxml")
            TicketsFormData = soup.findAll("tr",class_ = "MasterAction")

            #Я до сих пор в ахуе, но оно работает стабильно.
            #I HATE LIFE 
            info = [
                [(element.get('title'), element.get('href'), element.text) if "MasterActionLink" in element.get('class', [])
                    else (element.get('title'), element.get('href')) if element.name == 'a' 
                    else element.get('title') 
                    for element in action.find_all(['a', True]) 
                    if (element.get('title') or element.get('href')) and
                       "UnreadArticles" not in element.get('class', []) and 
                       "UnreadArticles Small" not in element.get('class', [])] for action in TicketsFormData]
            #I HATE LIFE

            #Приведение данных к удобному виду. 
            TicketsData = []
            for ticket in info:
                parsed_url = urlparse(OTRS_QUEUE)
                parsed_data = {"Link":f"{parsed_url.scheme}://{parsed_url.netloc}"+ticket[3][1],
                               "Number":ticket[3][2],
                               "Title":ticket[6],
                               "Sender":ticket[5],
                               "Client":ticket[13]}
                if ticket_exist(parsed_data["Number"]):
                    Log.console(f"Тикет {parsed_data["Number"]} уже был")
                    continue
                else:
                    TicketsData.append(parsed_data)
                    ticket_add(parsed_data["Number"], parsed_data["Link"])
                    Log.info(f"Новый тикет {parsed_data["Number"]}")
            return TicketsData
        except Exception as EXCEPTION:
            Log.critical(str(EXCEPTION))
            return False

