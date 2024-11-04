import datetime
from vk_api.utils import get_random_id
import requests
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from database import create_tables, Users, Find_Users, Favorites_Users
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from config import token_bot, user_token

DSN = 'postgresql://postgres:postgres@localhost:5432/nikolayshirokov'
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()

token = token_bot

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)  # РАБОТА С СООБЩЕНИЯМИ
keyboard_ontime = VkKeyboard(one_time=False)
keyboard_ontime.add_button('найти', color=VkKeyboardColor.SECONDARY)
keyboard_ontime.add_line()
keyboard_ontime.add_button('в избранное', color=VkKeyboardColor.POSITIVE)
keyboard_ontime.add_line()
keyboard_ontime.add_button('в избранном', color=VkKeyboardColor.POSITIVE)
keyboard_ontime.add_line()
keyboard_ontime.add_button('далее', color=VkKeyboardColor.POSITIVE)


def write_msg(user_id, message, keyboard=None):
    post = {
        'user_id': user_id,
        'message': message,
        'random_id': get_random_id()
    }
    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()

    vk.method('messages.send', post)


class VkUser:
    def __init__(self, id_user):

        self.id_user = id_user

    def get_user_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': token,
                  'user_ids': self.id_user,
                  'fields': 'first_name,bdate,city,sex',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        self.first_name = response['response'][0]['first_name']
        self.last_name = response['response'][0]['last_name']
        if response['response'][0]['sex'] == 1:
            self.sex = 'женский'
        if response['response'][0]['sex'] == 2:
            self.sex = 'мужской'
        self.city = self.get_city(response)
        self.id_city = self.get_id_city()
        self.age = self.get_age(response['response'][0])
        return [self.id_user, self.first_name, self.last_name, self.sex, self.city, self.id_city, self.age]

    def get_sex(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': token,
                  'user_ids': self.id_user,
                  'fields': 'first_name,bdate,city,sex',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        return response['response'][0]['sex']

    def get_city(self, result):
        for i in result['response']:
            if 'city' in i:
                city = i.get('city')
                title = city.get('title')
                return title
            else:
                write_msg(self.id_user, 'Введите название вашего города: ')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city = event.text
                        return city

    def get_id_city(self):
        """ПОЛУЧЕНИЕ ID ГОРОДА ПОЛЬЗОВАТЕЛЯ ПО НАЗВАНИЮ"""
        url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': user_token,
                  'q': f'{self.city}',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        information_list = response['response']
        id_city = information_list['items']
        return id_city[0]['id']

    def get_age(self, result):
        try:
            date_list = result['bdate'].split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            else:
                write_msg(self.id_user, 'Введите ваш возраст: ')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            age = event.text
                            return age
        except KeyError:
            write_msg(self.id_user, 'Введите ваш возраст: ')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        age = event.text
                        return age

    def find_user(self):
        """ПОИСК ЧЕЛОВЕКА ПО ПОЛУЧЕННЫМ ДАННЫМ"""
        url = f'https://api.vk.com/method/users.search'
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(),
                  'age_from': self.age,
                  'age_to': self.age,
                  'city': self.id_city,
                  'fields': 'is_closed, id, first_name, last_name',
                  'count': 1000}
        resp = requests.get(url, params=params)
        resp_json = resp.json()
        dict_1 = resp_json['response']
        list_1 = dict_1['items']
        for person_dict in list_1:
            if person_dict.get('is_closed') == False:
                self.first_name_user = person_dict.get('first_name')
                self.last_name_user = person_dict.get('last_name')
                self.vk_id_user = str(person_dict.get('id'))
                self.vk_link_user = 'vk.com/id' + str(person_dict.get('id'))
                session.add(
                    Find_Users(first_name_user=self.first_name_user, last_name_user=self.last_name_user,
                               vk_id_user=self.vk_id_user,
                               vk_link_user=self.vk_link_user))
                session.commit()
            else:
                continue
        return f'Поиск завершён'


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        if request == "привет":
            user1 = VkUser(event.user_id)
            id_user, first_name, last_name, sex, city, id_city, age = user1.get_user_info()
            write_msg(event.user_id, f"Хай, {first_name}, id - {id_user}\n"
                                     f"Ваш город - {city}\n"
                                     f"Ваш пол - {sex}\n"
                                     f"Ваш возраст - {age}\n\n"
                                     f"Нажми кнопку 'найти' и я выведу найденного человека", keyboard=keyboard_ontime)
            session.add(Users(id_user=id_user, first_name=first_name, last_name=last_name, age=age, sex=sex, city=city,
                              id_city=id_city))
            session.commit()
            user1.find_user()
        elif request == "найти":
            first = session.query(Find_Users).first()
            write_msg(event.user_id,
                      f'- {first.first_name_user} {first.last_name_user}\n'
                      f'- {first.vk_link_user}\n'
                      f'три фотографии')
        elif request == "далее":
            try:
                session.delete(first)
                session.commit()
                first = session.query(Find_Users).first()
                write_msg(event.user_id,
                          f'- {first.first_name_user} {first.last_name_user}\n'
                          f'- {first.vk_link_user}\n'
                          f'три фотографии')
            except AttributeError:
                write_msg(event.user_id, f'Людей больше не найдено')
        elif request == "в избранное":
            favorite = Favorites_Users(first_name_user=first.first_name_user, last_name_user=first.last_name_user,
                                       vk_id_user=first.vk_id_user, vk_link_user=first.vk_link_user)
            session.add(favorite)  # добавляем в бд
            session.commit()  # сохраняем изменения
            session.refresh(favorite)  # обновляем состояние объекта
            write_msg(event.user_id,
                      f'- {first.first_name_user} {first.last_name_user} добавлен(а) в избранное\n')
        elif request == "в избранном":
            favorites_users = session.query(Favorites_Users).all()
            for f_user in favorites_users:
                write_msg(event.user_id,
                          f'- {f_user.first_name_user} {f_user.last_name_user}\n'
                          f'- {f_user.vk_link_user}\n'
                          f'три фотографии')
        else:
            write_msg(event.user_id, "Не поняла вашего ответа...")
