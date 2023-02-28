import os
import sys

#モジュール探索パス追加
p = ['../','../../','../../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
import re
import requests
import database

class UserFunc():
    def __init__(self) -> None:
        pass
    
    #入力されたフレンドコード(SW)の確認
    def check_friendcode(self, friendcode:str) -> bool:
        r = re.search(r"^\d{4}-\d{4}-\d{4}$",friendcode)
        return bool(r)
    
    #入力されたTwitterIDの確認
    def check_twitterid(self, twitterid:str) -> bool:
        r = re.search("^[0-9a-zA-Z_]{1,15}$",twitterid)
        return bool(r)

class UserDBFunc():
    def __init__(self) -> None:
        self.db = database.Database()

    #指定ユーザの情報取得
    async def get_userdata(self, userid:str) -> list:
        r = await self.db.get_db(name='read', table='user-master', column='DiscordID', record=str(userid))
        ud = r.json()
        return ud

    #指定ユーザの情報送信
    async def post_userdata(self, userid:str, postdata:dict, apptype:int) -> requests.Response:
        r = await self.db.post_db(name='write', data=postdata, table='user-master', column='DiscordID', record=str(userid), apptype=apptype)
        return r
    
    #指定ユーザの情報送信をログ
    async def log_userdata(self, author:discord.User, postdata:dict, currenttime:str, apptype:int) -> requests.Response:
        datekey = ["登録日時", "最終更新日時"]
        for k in datekey:
            if k in postdata: del postdata[k]

        add = {"タイムスタンプ":currenttime, "申請区分":apptype, "実行者Discord名": str(author), "実行者DiscordID": str(author.id)}
        logdata = postdata|add
        r = await self.db.post_db(name='log', data=logdata, table='user-log')
        return r