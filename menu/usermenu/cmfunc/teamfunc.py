import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
import requests
import database

#コマンド実行者がリーダーか判断
def check_leader(author:discord.User) -> list:
    r = database.Database().get_db(name='read', tablename='team-master', subjectid=str(author.id))
    td = r.json()
    if td == False: return list()
    else: return td

#チーム情報送信
def apply_teamdata(author:discord.User, leader:discord.User, apptype:int, teamdata:dict) -> requests.Response:
    r = database.Database().post_db(name='apply', data=teamdata, tablename='team-master', apptype=apptype, authorname=str(author), authorid=str(author.id), subjectid=str(leader.id))
    return r

#チームメンバーのXPの取得
def get_teamxps(author:discord.User) -> list:
    r = database.Database().get_db(name='get_teamxps', leaderid=author.id)
    xps = r.json()
    if xps == False: return list()
    else: return xps

#チームの平均XP計算
def cal_averagexp(xps:list) -> int:
    f = 50
    xpsr = [int(xp/f)*f for xp in xps]
    xpavg = int(sum(xpsr)/len(xpsr))
    return xpavg