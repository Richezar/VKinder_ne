import datetime
from vk_api.utils import get_random_id
import requests
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from database import Users, Favorites, session
from config import token_bot, token_user
import operator

token = token_bot

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)  # РАБОТА С СООБЩЕНИЯМИ

keyboard_ontime = VkKeyboard(one_time=False)
keyboard_ontime.add_button('найти', color=VkKeyboardColor.SECONDARY)
keyboard_ontime.add_line()
keyboard_ontime.add_button('в избранное', color=VkKeyboardColor.POSITIVE)
keyboard_ontime.add_line()
keyboard_ontime.add_button('в избранном', color=VkKeyboardColor.POSITIVE)

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
        photo_album = [{'photo_link': file['id'], 'photo_likes': file['likes']['count']} for file in response['response']['items']]
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
            if person_dict.get('is_closed') == False:
                firstname_user = person_dict.get('first_name')
                lastname_user = person_dict.get('last_name')
                vkid_user = str(person_dict.get('id'))
                vklink_user = 'vk.com/id' + str(person_dict.get('id'))
                people.append([firstname_user, lastname_user, vkid_user, vklink_user])
            else:
                continue
        return people


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        if request == "привет":
            user1 = VkUser(event.user_id)
            id_user, first_name, last_name, sex, city, id_city, age = user1.get_user_info()
            if sex == 1:
                text_sex = 'женский'
            else:
                text_sex = 'мужской'
            write_msg(event.user_id, f"Привет, {first_name}, id - {id_user}\n"
                                     f"Ваш город - {city}\n"
                                     f"Ваш пол - {text_sex}\n"
                                     f"Ваш возраст - {age}\n\n"
                                     f"Нажми кнопку 'найти' и я покажу найденного человека", keyboard=keyboard_ontime)
            session.add(Users(id_user=id_user, first_name=first_name, last_name=last_name, age=age, sex=sex, city=city,
                              id_city=id_city))
            session.commit()
            count = -1
        elif request == "найти":
            try:
                count += 1
                list_people = user1.find_user()
                id_search = list_people[count][2]
                write_msg(event.user_id,
                          f'- {list_people[count][0]} {list_people[count][1]}\n'
                          f'- {list_people[count][3]}\n')
                photos3 = user1.get_photos(list_people[count][2])
                if photos3 != []:
                    user1.send_photos(photos3)
                else:
                    write_msg(event.user_id,
                              f'Фотографии не найдены')
            except IndexError:
                write_msg(event.user_id, f'Людей больше не найдено')
        elif request == "в избранное":
            existing_id_user = session.query(Favorites).filter_by(favorite_link_user=list_people[count][3]).first()
            if not existing_id_user:
                session.add(
                    Favorites(user_id=id_user, first_name=list_people[count][0], last_name=list_people[count][1],
                              favorite_link_user=list_people[count][3]))  # добавляем в бд
                session.commit()  # сохраняем изменения
                write_msg(event.user_id,
                          f'- {list_people[count][0]} {list_people[count][1]} добавлен(а) в избранное\n')
            else:
                write_msg(event.user_id, "Человек уже добавлен в избранное")
        elif request == "в избранном":
            result = session.query(Favorites.first_name, Favorites.last_name, Favorites.favorite_link_user).filter(Favorites.user_id == str(id_user)).all()
            for user in result:
                write_msg(event.user_id,
                        f'- {user[0]} {user[1]}\n'
                                f'- {user[2]}\n')
        else:
            write_msg(event.user_id, "Не поняла вашего ответа...")