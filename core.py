import vk_api
from vk_api.exceptions import ApiError
from config import acces_token
from datetime import datetime

class VkTools():

    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):

        try:
            info, = self.api.method('users.get', {
                'user_id': user_id,
                'fields': 'city,bdate,sex,relation,home_town'
            })
        except ApiError as error:
            info = {}
            print(f'error = {error}')
        user_info = {
            'id': info.get('id'),
            'first_name': info.get('first_name'),
            'last_name': info.get('last_name'),
            'bdate': info.get('bdate'),
            'home_town': info.get('home_town'),
            'sex': info.get('sex'),
            'city_id': info.get('city')['id'] if info.get('city') is not None else None
        }
        return user_info

    def search_users(self, params, offset):
        sex = 1 if params['sex'] == 2 else 2
        city_id = params['city_id']
        current_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5
        try:
            users = self.api.method(
                'users.search', {
                    'count': 10,
                    'offset': offset,
                    'age_from': age_from,
                    'age_to': age_to,
                    'sex': sex,
                    'city': city_id,
                    'status': 6,
                    'is_closed': False
                    # 'online': 1
                })
        except ApiError as error:
            users = {}
            print(f'error = {error}')
        users = users.get('items') if users.get('items') is not None else []
        res = []
        for user in users:
            if user['is_closed'] == False:
                res.append({
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name']
                })
        return res

    def get_photos(self, user_id):
        try:
            photos = self.api.method('photos.get',
                                     {'user_id': user_id,
                                      'album_id': 'profile',
                                      'extended': 1
                                     })
        except ApiError as error:
            photos = {}
            print(f'error = {error}')
        photos = photos.get('items') if photos.get('items') is not None else []

        res = []
        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        })
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res

    def get_city_id(self, name_city, name_reg=None):
        city_id = None
        try:
            query = self.api.method(
                'database.getCities', {
                    'country_id': 1,
                    'q': name_city
                })
        except ApiError as error:
            query = {}
            print(f'error = {error}')
        citys = query.get('items') if query.get('items') is not None else []
        
        if name_reg is not None:
            for city in citys:
                if city['title'].lower() == name_city and city.get('region') == None:
                    city_id = city['id']
                    continue
                if city['title'].lower() == name_city and city['region'].lower() == name_reg:
                    city_id = city['id']
            return city_id
        elif query['count'] == 1:
            city_id = citys[0]['id']
            return city_id
        elif name_city == 'москва' or name_city == 'мск':
            return 1
        elif name_city == 'санкт-петербург' or name_city == 'спб':
            return 2

if __name__ == '__main__':
    current_time = datetime.now()
    print(current_time)
    bot = VkTools(acces_token)
    params = bot.get_profile_info(2623247) #427136097 2623247 13954734
    print(params)
    users = bot.search_users(params, offset=0)
    print(users)
    print(bot.get_city_id('киров', 'кировская область'))
    print(bot.get_city_id('москва'))
    print(bot.get_city_id('киров-чепецк'))
    print(bot.get_city_id('санкт-петербург'))
    print(bot.get_city_id('краснодар'))
    print(bot.get_city_id('орехово-зуево'))
    print(bot.get_city_id('мск'))