import os
import sys

#モジュール探索パス追加
p = ['../','../../']
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
def check_friendcode(friendcode:int) -> bool:
    d = 12 #受付桁数
    if friendcode < 0 or len(str(friendcode)) != d: return False
    else: return True

#入力されたフレンドコード(int)から指定の文字列形式に変換
def convert_friendcode(friendcode:int) -> str:
    l = re.split('(....)',str(friendcode))[1::2]
    converted = '-'.join(l)
    return converted

#入力されたTwitterIDの確認
def check_twitterid(twitterid:str) -> bool:
    r = re.search("@[0-9a-zA-Z_]{1,15}",twitterid)
    if twitterid != r.group(): return False
    else: return True

#ユーザ情報送信
def apply_userdata(author:discord.User, user:discord.User, apptype:int, userdata:dict) -> requests.Response:
    r = database.Database().post_db(name='apply', data=userdata, tablename='indiv-master', apptype=apptype, authorname=str(author), authorid=str(author.id), subjectid=str(user.id))
    return r
