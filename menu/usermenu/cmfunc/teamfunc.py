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
    f = 50 #切り捨て値
    xpld = sorted(xps, reverse=True) #XP降順リスト
    xpsr = [int(xp/f)*f for xp in xpld[:4]] #該当XPを指定規格に変換
    xpavg = int(sum(xpsr)/len(xpsr)) #平均XP算出
    return xpavg

##NEW##
#チーム情報の取得
def get_teamdata(authorid:str) -> list:
    r = database.Database().get_db(name='read', tablename='team-master', columnname='リーダーID', subjectrecord=str(authorid))
    td = r.json()
    if td == False: return list()
    else: return td