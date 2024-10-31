import datetime
from vk_api.utils import get_random_id
import requests
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from database import Users, session
from config import token_bot

token = token_bot

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)  # РАБОТА С СООБЩЕНИЯМИ

keyboard_ontime = VkKeyboard(one_time=False)
keyboard_ontime.add_button('найти', color=VkKeyboardColor.SECONDARY)
keyboard_ontime.add_button('избранное', color=VkKeyboardColor.POSITIVE)

def write_msg(user_id, message, keyboard=None):
    post = {
            'user_id': user_id,
            'message': message,
            'random_id': get_random_id()
            }
    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()

    vk.method('messages.send', post)

class VkUser():
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
        self.age = self.get_age(response['response'][0])
        return [self.id_user, self.first_name, self.last_name, self.sex, self.city, self.age]

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
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            write_msg(self.id_user, 'Введите ваш возраст: ')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return age



for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        if request == "привет":
            user1 = VkUser(event.user_id)
            id_user, first_name, last_name, sex, city, age = user1.get_user_info()
            write_msg(event.user_id, f"Хай, {first_name}, id - {id_user}\n"
                                     f"Ваш город - {city}\n"
                                     f"Ваш пол - {sex}\n"
                                     f"Ваш возраст - {age}\n", keyboard=keyboard_ontime)
            session.add(Users(id_user=id_user, first_name=first_name, last_name=last_name, age=age, sex=sex, city=city))
            session.commit()
        elif request == "пока":
            write_msg(event.user_id, "Пока((")
        else:
            write_msg(event.user_id, "Не поняла вашего ответа...")