import os
import sys

#モジュール探索パス追加
p = ['../','../../','../../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
import re
import requests
import database

#指定ユーザのデータ確認
def check_userdata(user:discord.User) -> list:
    r = database.Database().get_db(name='read', tablename='indiv-master', subjectid=str(user.id))
    ud = r.json()
    if ud == False: return list()
    else: return ud

#入力されたフレンドコードの確認
def check_friendcode(friendcode:str) -> bool:
    r = re.search(r"\d{4}-\d{4}-\d{4}",friendcode)
    return bool(r)

#入力されたTwitterIDの確認
def check_twitterid(twitterid:str) -> bool:
    r = re.search("@[0-9a-zA-Z_]{1,15}",twitterid)
    return bool(r)

#ユーザ情報送信
def apply_userdata(author:discord.User, user:discord.User, apptype:int, userdata:dict) -> requests.Response:
    r = database.Database().post_db(name='apply', data=userdata, tablename='indiv-master', apptype=apptype, authorname=str(author), authorid=str(author.id), subjectid=str(user.id))
    return r
