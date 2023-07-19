import requests
import json
import datetime
from tqdm import tqdm
import time

with open('token_yandex.txt', 'r') as file_yandex:
    token_yandex = file_yandex.readline()

with open('token_vk.txt', 'r') as file_vk:
    token_vk = file_vk.readline()

url_yandex = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

url_vk = 'https://api.vk.com/method/photos.get'

url_folder_create = 'https://cloud-api.yandex.net/v1/disk/resources'

class Vk:
    def __init__(self, token_vk, user_id, version = '5.131'):
        self.token = token_vk
        self.version = version
        self.id = user_id
        self.params = {'access_token': self.token, 'v': self.version, 'owner_id': self.id}
        self.size_for_upload = {}

    def get_response(self, url):
        params = {
            'extended': 1,
            'photo_sizes': 0,
            'album_id': 'profile',
            'rev': 0
        }
        response = requests.get(url, params = {**self.params, **params})
        for i in tqdm(range(100), desc = 'Получение данных с профиля пользователя'):
            time.sleep(0.1)
        response_get = response.json()
        if response_get['response']['items'] == []:
            return None
        else:
            return response_get

    def vk_download(self, response):
        for i in response['response']['items']:
            dict = {}
            for n, j in enumerate(i['sizes']):
                dict[j['width']] = n
                max_dict = max(dict.keys())
            for n, j in enumerate(i['sizes']):
                if j['width'] == 0 and j['type'] == 'w':
                    self.size_for_upload[j['url']] = [
                        i['likes']['count'],
                        datetime.datetime.fromtimestamp(i['date']).strftime('%Y-%m-%d'),
                        i['sizes'][n]['type']
                    ]
                elif n == dict[max_dict]:
                    self.size_for_upload[j['url']] = [
                        i['likes']['count'],
                        datetime.datetime.fromtimestamp(i['date']).strftime('%Y-%m-%d'),
                        i['sizes'][n]['type']
                    ]
        for n in tqdm(range(100), desc = 'Обработка полученных данных для загрузки на Яндекс.Диск'):
            time.sleep(0.1)
        return self.size_for_upload


class YaUploader:
    def __init__(self, token: str):
        self.token = token
        self.params = {}
        self.name_folder = ''

    def create_folder(self, url):
        self.name_folder = input('Создайте папку на Яндекс.Диск(введите название): ')
        headers = {
            'Authorization': self.token
        }
        path = {
            'path': str(self.name_folder)
        }
        response = requests.put(url, headers=headers, params=path)

    def upload(self, url, list_params):
        headers = {
            'Authorization': self.token
        }
        list_count = [i[0] for i in list_params.values()]
        dict_params_count = {i[0]: list_count.count(i[0]) for i in list_params.values()}
        count = 1
        for i in tqdm(list_params, desc = 'Загрузка объектов на Яндекс.Диск'):
            for j in dict_params_count:
                if dict_params_count[list_params[i][0]] > 1:
                    self.params['url'] = str(i)
                    self.params['path'] = str(self.name_folder + '/') + str(list_params[i][0]) + '.' + str(list_params[i][1]) + '.jpg'
                else:
                    self.params['url'] = str(i)
                    self.params['path'] = str(self.name_folder + '/') + str(list_params[i][0]) + '.jpg'

            response_yandex = requests.post(url, headers=headers, params=self.params)
            if 200 <= response_yandex.status_code < 300:
                data = {}
                name = 'file' + '_' + str(count) + '.json'
                data['file_name'] = self.params['path'].replace(str(self.name_folder) + '/', '')
                data['size'] = list_params[self.params['url']][2]
                with open(name, 'w') as f:
                    json.dump(data, f, ensure_ascii=False, indent = 2)
                    time.sleep(1)
                    for j in tqdm(range(100), desc=f'Запись данных об объекте {count} в файл {name}'):
                        pass
                    count += 1
                    time.sleep(1)
            else:
                print(f'Возникла ошибка {response_yandex.status_code}')
                break


user = input('Введите id пользователя: ')
if user.isdigit() is True:
    vk_res = Vk(token_vk, user)
    vk_1 = vk_res.get_response(url_vk)
    time.sleep(1)
    if vk_1 is None:
        print(f'Error: у пользователя с id {user} отсутствуют фотографии')
    else:
        vk_2 = vk_res.vk_download(vk_1)
        time.sleep(1)
        yandex_load = YaUploader(token_yandex)
        time.sleep(1)
        create = yandex_load.create_folder(url_folder_create)
        time.sleep(1)
        upload = yandex_load.upload(url_yandex, vk_2)
else:
    print('Error: id пользователя состоит из цифр')