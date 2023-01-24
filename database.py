import os
import json
import requests

class Database():
    def __init__(self):
        self.url = os.getenv('GAS_PROJECT_URL')+'?'

    #DBへのPOST処理
    def post_db(self, name:str, data, **kwargs) -> requests.Response:
        base = {'name':name}
        payload = base|kwargs
        output = requests.post(url=self.url, params=payload, data=json.dumps(data))
        return output

    #DBへのGET処理
    def get_db(self, name:str, **kwargs) -> requests.Response:
        base = {'name':name}
        payload = base|kwargs
        output = requests.get(url=self.url, params=payload)
        return output