import time
from typing import Union
import requests
from hashlib import md5
from typing import Union
from urllib.parse import urlencode
from requests_toolbelt.multipart.encoder import MultipartEncoder
import imghdr

UID = 1772442517  # 你的UID
ACCESS_KEY = "8c71b6f544ed4181046117c3efe406c2"  # 你的ACCESS_KEY (TV端,非TV端自行更换下面的APPKEY,APPSECRET,TV端access_key获取工具 https://github.com/XiaoMiku01/fansMedalHelper/releases/tag/logintool)
FACE_PATH = r"face.jpg"  # 头像路径 推荐正方形
BG_PATH = r"background.jpg"  # 背景图路径 推荐 9:16 竖版原图 效果非常好


class Crypto:

    APPKEY = '4409e2ce8ffd12b8'
    APPSECRET = '59b43e04ad6965f34319062b478f83dd'

    @staticmethod
    def md5(data: Union[str, bytes]) -> str:
        '''generates md5 hex dump of `str` or `bytes`'''
        if type(data) == str:
            return md5(data.encode()).hexdigest()
        return md5(data).hexdigest()

    @staticmethod
    def sign(data: Union[str, dict]) -> str:
        '''salted sign funtion for `dict`(converts to qs then parse) & `str`'''
        if isinstance(data, dict):
            _str = urlencode(data)
        elif type(data) != str:
            raise TypeError
        return Crypto.md5(_str + Crypto.APPSECRET)


class SingableDict(dict):
    @property
    def sorted(self):
        '''returns a alphabetically sorted version of `self`'''
        return dict(sorted(self.items()))

    @property
    def signed(self):
        '''returns our sorted self with calculated `sign` as a new key-value pair at the end'''
        _sorted = self.sorted
        return {**_sorted, 'sign': Crypto.sign(_sorted)}


def get_image_type(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    return imghdr.what(None, data)


def upload_image(file_path):
    url = "https://api.bilibili.com/x/upload/app/image?access_key=" + ACCESS_KEY

    payload = {'bucket': 'medialist', 'dir': 'nft'}

    with open(file_path, 'rb') as f:
        type = f'image/{imghdr.what(f)}'
        print(type)
        files = [
            (
                'file',
                (file_path, f, type),
            )
        ]
        response = requests.request("POST", url, data=payload, files=files)
        print(response.text)
        return response.json()['data']['location']


def get_one_card_id():
    url = "https://api.bilibili.com/x/vas/nftcard/cardlist"
    params = SingableDict(
        {
            "access_key": ACCESS_KEY,
            "act_id": "4",
            "appkey": "4409e2ce8ffd12b8",
            "disable_rcmd": "0",
            "ruid": UID,
            "statistics": "{\"appId\":1,\"platform\":3,\"version\":\"7.9.0\",\"abtest\":\"\"}",
            "ts": int(time.time()),
        }
    ).signed
    response = requests.request("GET", url, params=params)
    data = response.json()
    if data['code'] != 0:
        print(data)
        return
    for round in data['data']['round_list']:
        for card in round['card_list']:
            if card['card_type'] == 1 and card['card_id_list']:
                print(card['card_id_list'][0]['card_id'])
                return card['card_id_list'][0]['card_id']
    print('没有 R 级别胶囊计划的卡片')
    return None


def set_face(card_id):
    api = "https://api.bilibili.com/x/member/app/face/digitalKit/update"
    params = SingableDict(
        {
            "access_key": ACCESS_KEY,
            "appkey": "4409e2ce8ffd12b8",
            "build": "7090300",
            "c_locale": "zh_CN",
            "channel": "xiaomi",
            "disable_rcmd": "0",
            "mobi_app": "android",
            "platform": "android",
            "s_locale": "zh_CN",
            "statistics": "{\"appId\":1,\"platform\":3,\"version\":\"7.9.0\",\"abtest\":\"\"}",
            "ts": int(time.time()),
        }
    ).signed
    m = MultipartEncoder(
        fields={
            'digital_kit_id': str(card_id),
            'face': ('face', open(FACE_PATH, 'rb'), 'application/octet-stream'),
        }
    )
    headers = {
        "Content-Type": m.content_type,
    }
    response = requests.request("POST", api, data=m, headers=headers, params=params)
    if response.json()['code'] != 0:
        print(response.json())
        return
    print('设置头像成功, 请等待审核')


def set_bg_img(img_url, card_id):
    api = "https://app.bilibili.com//x/v2/space/digital/bind"
    data = SingableDict(
        {
            "access_key": ACCESS_KEY,
            "appkey": "4409e2ce8ffd12b8",
            "build": "7090300",
            "c_locale": "zh_CN",
            "card_id": card_id,
            "channel": "xiaomi",
            "disable_rcmd": "0",
            "img_url": img_url,
            "mobi_app": "android",
            "platform": "android",
            "s_locale": "zh_CN",
            "space_bg_type": "1",
            "statistics": "{\"appId\":1,\"platform\":3,\"version\":\"7.9.0\",\"abtest\":\"\"}",
            "ts": int(time.time()),
        }
    ).signed
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }
    response = requests.request("POST", api, data=data, headers=headers)
    if response.json()['code'] != 0:
        print(response.json())
        return
    print('设置背景成功')


def main():
    card_id = get_one_card_id()
    if not card_id:
        return
    img_url = upload_image(BG_PATH)
    set_bg_img(img_url, card_id)
    # set_face(card_id)


if __name__ == '__main__':
    main()