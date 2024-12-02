from vk_api.longpoll import VkEventType
from database import Users, Favorites, session
from keyboard import keyboard_ontime

from vkapi import VkUser, write_msg, longpoll


def msg_bot():
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
                                         f"Нажми кнопку 'найти' и я покажу найденного человека",
                          keyboard=keyboard_ontime)
                session.add(
                    Users(id_user=id_user, first_name=first_name, last_name=last_name, age=age, sex=sex, city=city,
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
                    photos3 = user1.get_photos(id_search)
                    if photos3:
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
                result = session.query(Favorites.first_name, Favorites.last_name, Favorites.favorite_link_user).filter(
                    Favorites.user_id == str(id_user)).all()
                for user in result:
                    write_msg(event.user_id,
                              f'- {user[0]} {user[1]}\n'
                              f'- {user[2]}\n')
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")


if __name__ == "__main__":
    msg_bot()
