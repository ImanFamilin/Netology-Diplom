import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import comunity_token, acces_token
from core import VkTools
from datetime import datetime
from data_store import DataStore
from config import file_db

class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.users = []
        self.offset = 0
        self.age = 10
        self.db = DataStore(file_db)

    def message_send(self, user_id, message, keyboard=None, attachment=None):
        
        query = {
            'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': get_random_id()
            }
        if keyboard != None:
            query.update({'keyboard': keyboard.get_keyboard()})
        self.vk.method('messages.send', query)

    def event_handler(self):
        context = 'standart'
        last_writer = None
        age_pass = False
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.params = self.vk_tools.get_profile_info(event.user_id)
                # self.params.update({'bdate': '15.09'})
                # self.params.update({'bdate': None})
                current_time = datetime.now()
                print(f'{current_time} id{self.params.get("id")} {self.params.get("first_name")} {self.params.get("last_name")} {event.text}')
                command = event.text.lower().split()
                if context == 'standart':
                    if self.params['id'] != last_writer:
                        self.users.clear()
                        self.offset = 0
                        age_pass = False
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Поиск', VkKeyboardColor.PRIMARY)

                    if 'привет' in command:
                        self.message_send(event.user_id, f'Здравствуйте, {self.params["first_name"]}!')
                        self.message_send(event.user_id, 'Чтобы искать людей, нажмите кнопку "Поиск"!', keyboard)
                    elif 'поиск' in command:
                        if self.params['bdate'] is not None and len(self.params['bdate'].split('.')) == 3 or age_pass == True:
                            self.message_send(event.user_id, 'Начинаю поиск...')
                            if len(self.users) == 0:
                                self.users = self.vk_tools.search_users(self.params, offset=self.offset, age=self.age)
                                self.offset += 10
                            if len(self.users) > 0:
                                user = self.users.pop()
                            while self.db.check_data(user['id'], event.user_id) is not None:
                                if len(self.users) == 0:
                                    self.users = self.vk_tools.search_users(self.params, offset=self.offset, age=self.age)
                                    self.offset += 10
                                if len(self.users) > 0:
                                    user = self.users.pop()
                            # здесь логика для проверки бд
                            photos_user = self.vk_tools.get_photos(user['id'])
                            attachment = ''
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                if num == 2:
                                    break
                            self.message_send(event.user_id, f'Встречайте {user["first_name"]} @id{user["id"]}', attachment=attachment)
                            self.message_send(event.user_id, 'Чтобы продолжить искать, снова нажмите кнопку!', keyboard)
                            print(self.users)
                            print(user)
                            print(self.offset)
                            print(self.age)
                            print(age_pass)
                            # здесь логика для добавления в бд
                            self.db.add_data(user['id'], event.user_id)
                        else:
                            self.message_send(event.user_id, f'{self.params["first_name"]}, я не нашел информации о вашем возрасте! Напишите ваш возраст числом')
                            context = 'input_age'
                        last_writer = self.params.get('id')
                    elif 'пока' in command:
                        self.message_send(event.user_id, f'До свидания, {self.params["first_name"]}!')
                    else:
                        self.message_send(event.user_id, 'Неизвестная команда!')
                        self.message_send(event.user_id, 'Чтобы искать людей, нажмите кнопку "Поиск"!', keyboard)
                elif context == 'input_age':
                    if event.text.isdigit():
                        age = int(event.text)
                        if age >= 10 and age <= 100:
                            self.age = age
                            self.message_send(event.user_id, 'Принято! Чтобы продолжить искать, снова нажмите кнопку!', keyboard)
                            context = 'standart'
                            age_pass = True
                        else:
                            self.message_send(event.user_id, 'Укажите возраст от 10 до 100!')
                    else:
                        self.message_send(event.user_id, 'Неверные данные!')
                elif context == 'input_city':
                    pass

if __name__ == '__main__':
    current_time = datetime.now()
    print(current_time)
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
