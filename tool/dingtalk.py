import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json
from tool.config import Config


class DingTalk:

    def __init__(self, secret=None, access_token=None):
        _config = Config()
        self.base_url = 'https://oapi.dingtalk.com/robot/send'
        self.secret = secret if secret else _config.get_str('ding.secret')
        self.access_token = access_token if access_token else _config.get_str('ding.access')

    def sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def get_url(self):
        timestamp, sign = self.sign()
        return f'{self.base_url}?access_token={self.access_token}&timestamp={timestamp}&sign={sign}'

    def send_text(self, msg, msg_type: str = 'text'):
        if msg_type == 'text':
            msg_json = {
                "msgtype": 'text',
                "text": {
                    "content": msg
                }
            }
        elif msg_type == 'markdown':
            msg_json = {
                "msgtype": 'markdown',
                "markdown": {
                    "title": '' if 'title' not in msg else msg.get('title'),
                    "text": msg.get('text')
                }
            }
        else:
            raise ValueError(f'msg_type {msg_type} not supported')
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        return requests.post(self.get_url(), data=json.dumps(msg_json), headers=header)
