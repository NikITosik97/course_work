import requests
from ACCESSTOKEN import access_token as VKTOKEN
from tqdm import tqdm
import json
from datetime import datetime
from TOKEN import TOKEN


class Backup:

    def __init__(self, id_user, token, count_photo=5):
        self.id_user = id_user
        self.token = token
        self.count_photo = count_photo
        self.count_photo_profile = 0
        self.name_photo = {"file_name": '', "size": ''}
        self.lst_likes = []
        self.url_photo = ''
        self.result = None

    def get_information_on_photos_vk(self):
        base_url = "https://api.vk.com/method/photos.get"

        params = {
            "access_token": VKTOKEN,
            "v": '5.131',
            "owner_id": self.id_user,
            "album_id": 'profile',
            "extended": 1,
            "photo_sizes": 1,
            "count": self.count_photo,
            "rev": 1
        }

        response = requests.get(url=base_url, params=params)

        self.result = response.json()

        self.count_photo_profile = self.result["response"]["count"]

    def create_folder_yandex_disk(self):
        base_url_create_folder = "https://cloud-api.yandex.net/v1/disk/resources"

        headers = {
            "Authorization": TOKEN
        }

        params = {
            "path": "disk:/course_paper"
        }

        response_yandex = requests.put(url=base_url_create_folder, params=params, headers=headers)

    def create_json_file_name(self):
        with open("info_photo.json", "w", encoding="utf-8") as file:
            info_photo_result = json.loads("[]")
            json.dump(info_photo_result, file, indent=4, ensure_ascii=False)

    def backup_copy(self):
        if self.count_photo_profile >= 5:
            self.count_photo_profile = 5
        else:
            self.count_photo_profile = self.result["response"]["count"]

        for i in tqdm(range(self.count_photo_profile), colour='#98FB98'):

            for j in self.result["response"]["items"][i]["sizes"]:
                if j["type"] == "w":
                    self.name_photo["size"] = j["type"]
                    self.url_photo = j["url"]
                    self.lst_likes.append(self.result["response"]["items"][i]["likes"]["count"])
                    if self.lst_likes.count(self.result["response"]["items"][i]["likes"]["count"]) == 1:
                        self.name_photo["file_name"] = self.result["response"]["items"][i]["likes"]["count"]
                    else:
                        self.name_photo["file_name"] = datetime.now()

            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

            headers = {
                "Authorization": TOKEN
            }

            response_upload = requests.post(url=upload_url,
                                            params={"url": self.url_photo,
                                                    "path": f"disk:/course_paper/{self.name_photo['file_name']}.jpg"},
                                            headers=headers)

            with open("info_photo.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                data.append({"file_name": f"{self.name_photo['file_name']}.jpg", "size": self.name_photo["size"]})

                with open("info_photo.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    backup = Backup(input("Введите ID пользователя: "), input("Введите TOKEN Яндекс Диска: "))
    backup.get_information_on_photos_vk()
    backup.create_folder_yandex_disk()
    backup.create_json_file_name()
    backup.backup_copy()
