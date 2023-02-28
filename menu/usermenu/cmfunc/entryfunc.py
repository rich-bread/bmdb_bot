import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import requests
import database

class EntryDBFunc():
    def __init__(self) -> None:
        self.db = database.Database()

    async def get_seasondata(self) -> list:
        r = await self.db.get_db(name='get_seasondata', period='entry')
        sd = r.json()
        return sd
    
    #参加申請情報をログ
    async def log_entrydata(self, logdata:dict) -> requests.Response:
        r = await self.db.post_db(name='log', data=logdata, table='entry-log')
        return r