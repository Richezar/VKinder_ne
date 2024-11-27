from datetime import datetime

import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
import operator
from config import token_user, token_bot
from vk_api.utils import get_random_id

token = token_bot
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


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
        self.sex = response['response'][0]['sex']
        self.city = self.get_city(response)
        self.id_city = self.get_id_city()
        self.age = self.get_age(response['response'][0])
        return [self.id_user, self.first_name, self.last_name, self.sex, self.city, self.id_city, self.age]

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
        url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': token_user,
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
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            write_msg(self.id_user, 'Введите ваш возраст: ')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return age

    def get_photos(self, user_id, photo_numb=3):
        url = f'https://api.vk.com/method/photos.get'
        params = {'access_token': token_user,
                  'owner_id': user_id,
                  'album_id': 'profile',
                  'extended': '1',
                  'rev': '0',
                  'v': '5.199'
                  }
        response = requests.get(url, params=params).json()
        photo_album = [{'photo_link': file['id'], 'photo_likes': file['likes']['count']} for file in
                       response['response']['items']]
        photo_album = sorted(photo_album, key=operator.itemgetter('photo_likes'), reverse=True)
        if len(photo_album) > 3:
            photo_album = photo_album[:photo_numb]
        photo_links = [f'photo{user_id}_{link["photo_link"]}' for link in photo_album]
        return photo_links

    def send_photos(self, photos):
        p = ''
        for photo in photos:
            p += photo + ','
        vk.method('messages.send', {'user_id': self.id_user,
                                    'access_token': token_user,
                                    'attachment': p,
                                    'random_id': 0})

    def find_user(self):
        """ПОИСК ЧЕЛОВЕКА ПО ПОЛУЧЕННЫМ ДАННЫМ"""
        url = f'https://api.vk.com/method/users.search'
        if self.sex == 1:
            search_sex = 2
        else:
            search_sex = 1
        params = {'access_token': token_user,
                  'v': '5.131',
                  'sex': search_sex,
                  'age_from': self.age,
                  'age_to': self.age,
                  'city': self.id_city,
                  'fields': 'is_closed, id, first_name, last_name',
                  'count': 1000}
        resp = requests.get(url, params=params).json()
        list_1 = resp['response']['items']
        people = []
        for person_dict in list_1:
            if not person_dict.get('is_closed'):
                firstname_user = person_dict.get('first_name')
                lastname_user = person_dict.get('last_name')
                vkid_user = str(person_dict.get('id'))
                vklink_user = 'vk.com/id' + str(person_dict.get('id'))
                people.append([firstname_user, lastname_user, vkid_user, vklink_user])
            else:
                continue
        return people
