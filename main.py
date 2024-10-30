import datetime
from random import randrange
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from database import create_tables, Users
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

DSN = 'postgresql://postgres:postgres@localhost:5432/test'
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()

token = '---'

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)  # РАБОТА С СООБЩЕНИЯМИ


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


def get_name(user_id):
    """ПОЛУЧЕНИЕ ИМЕНИ ПОЛЬЗОВАТЕЛЯ, КОТОРЫЙ НАПИСАЛ БОТУ"""
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': token,
              'user_ids': user_id,
              'v': '5.131'}
    repl = requests.get(url, params=params)
    response = repl.json()
    information_dict = response['response']
    for i in information_dict:
        for key, value in i.items():
            first_name = i.get('first_name')
            return first_name


def get_city(user_id):
    """ПОЛУЧЕНИЕ ГОРОДА ПОЛЬЗОВАТЕЛЯ, КОТОРЫЙ НАПИСАЛ БОТУ"""
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': token,
              'user_ids': user_id,
              'fields': 'city',
              'v': '5.131'}
    repl = requests.get(url, params=params)
    response = repl.json()
    information_dict = response['response']
    for i in information_dict:
        if 'city' in i:
            city = i.get('city')
            title = city.get('title')
            # id = str(city.get('id'))
            return title
        else:
            write_msg(user_id, 'Введите название вашего города: ')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:

                    if event.to_me:
                        city = event.text
                        return city


def get_sex(user_id):
    """ПОЛУЧЕНИЕ  ПОЛА ПОЛЬЗОВАТЕЛЯ, КОТОРЫЙ НАПИСАЛ БОТУ"""
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': token,
              'user_ids': user_id,
              'fields': 'sex',
              'v': '5.131'}
    repl = requests.get(url, params=params)
    response = repl.json()
    sex = response['response'][0]['sex']
    if sex == 1:
        return 'женский'
    elif sex == 2:
        return 'мужской'
    else:
        write_msg(user_id, 'Введите ваш пол: ')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    sex = event.text
                    return sex


def get_age(user_id):
    """ПОЛУЧЕНИЕ ВОЗРАСТА ПОЛЬЗОВАТЕЛЯ """
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': token,
              'user_ids': user_id,
              'fields': 'bdate',
              'v': '5.131'}
    repl = requests.get(url, params=params)
    response = repl.json()
    year = response['response'][0]['bdate']
    date_list = year.split('.')
    if len(date_list) == 3:
        year = int(date_list[2])
        year_now = int(datetime.date.today().year)
        return year_now - year
    else:
        write_msg(user_id, 'Введите ваш возраст: ')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    age = event.text
                    return age


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                id_user = event.user_id
                city = get_city(event.user_id)
                sex = get_sex(event.user_id)
                age = get_age(event.user_id)
                write_msg(event.user_id, f"Хай, {get_name(event.user_id)}, id - {id_user}\n"
                                         f"Ваш город - {city}\n"
                                         f"Ваш пол - {sex}\n"
                                         f"Ваш возраст - {age}\n")
                session.add(Users(id_user=id_user, age=age, sex=sex, city=city))
                session.commit()
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")