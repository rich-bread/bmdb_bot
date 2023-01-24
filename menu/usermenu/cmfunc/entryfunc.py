import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
import requests
import database

#コマンド実行者がリーダーか判断
def check_season() -> list:
    r = database.Database().get_db(name='get_seasondata')
    sd = r.json()
    if sd == False: return list()
    else: return sd

#参加申請送信
def apply_entrylog(author:discord.User, entryparam:int, timestamp:str, entrylog:dict) -> requests.Response:
    r = database.Database().post_db(name='entry', data=entrylog, entryparam=entryparam, authorname=str(author), authorid=str(author.id), timestamp=timestamp)
    return r