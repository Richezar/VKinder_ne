import datetime
from random import randrange

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import Token

token = Token

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
    information_dict = response['response']
    for i in information_dict:
        sex = i.get('sex')
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
    url = url = f'https://api.vk.com/method/users.get'
    params = {'access_token': token,
              'user_ids': user_id,
              'fields': 'bdate',
              'v': '5.131'}
    repl = requests.get(url, params=params)
    response = repl.json()
    information_dict = response['response']
    for i in information_dict:
        date = i.get('bdate')
        date_list = date.split('.')
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
                write_msg(event.user_id, f"Хай, {get_name(event.user_id)},id {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            elif request == "город":
                write_msg(event.user_id, f"Ваш город {get_city(event.user_id)}")
            elif request == "пол":
                write_msg(event.user_id, f"Ваш пол {get_sex(event.user_id)}")
            elif request == "возраст":
                write_msg(event.user_id, f"Ваш возраст {get_age(event.user_id)}")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
