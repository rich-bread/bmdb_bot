import os
import json
import requests
import aiohttp
import asyncio

class Database():
    def __init__(self):
        self.url = os.getenv('GAS_PROJECT_URL')+'?'

    #DBへのPOST処理
    async def post_db(self, name:str, data:dict, **kwargs) -> requests.Response:
        base = {'name':name}
        payload = base|kwargs
        output = requests.post(url=self.url, params=payload, data=json.dumps(data))
        return output

    #DBへのGET処理
    async def get_db(self, name:str, **kwargs) -> requests.Response:
        base = {'name':name}
        payload = base|kwargs
        output = requests.get(url=self.url, params=payload)
        return output
    
class NewDatabase():
    def __init__(self):
        self.url = os.getenv('GAS_PROJECT_URL')+'?'

    #DBへのPOST処理
    async def post_db(self, name:str, data:dict, **kwargs) -> requests.Response:
        async with aiohttp.ClientSession.post(url=self.url) as r:
            base = {'name':name}
            payload = base|kwargs
