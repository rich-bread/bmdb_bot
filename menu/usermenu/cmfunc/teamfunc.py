import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
import requests
import database
from cmmod.json_module import open_json

##NEW##
#チーム情報の取得
def get_teamdata(authorid:str) -> list:
    r = database.Database().get_db(name='read', tablename='team-master', columnname='リーダーID', subjectrecord=str(authorid))
    td = r.json()
    if td == False: return list()
    else: return td

class TeamFunc():
    def __init__(self) -> None:
        pass
    
    #(旧)チームの平均XP計算
    def old_cal_averagexp(self, xps:list) -> int:
        f = 50 #切り捨て値
        xpld = sorted(xps, reverse=True) #XP降順リスト
        xpsr = [int(xp/f)*f for xp in xpld[:4]] #該当XP(=XP上位4名)を指定規格に変換
        xpavg = int(sum(xpsr)/len(xpsr)) #平均XP算出
        return xpavg
    
    #チームの平均XP計算
    def cal_averagexp(self, xps:list) -> int:
        xpld = sorted(xps, reverse=True) #XP降順リスト
        xpavg = int(sum(xpld[:4])/len(xpld[:4])) #平均XP算出
        return xpavg
    
    #チームメンバーのXPリスト作成
    def col_memberxps(self, userdata:list) -> list:
        f = open_json('')

class TeamDBFunc():
    def __init__(self) -> None:
        self.db = database.Database()

    #指定チームの情報取得
    async def get_teamdata(self, leaderid:str) -> list:
        r = await self.db.get_db(name='read', table='team-master', column='リーダー', record=str(leaderid))
        td = r.json()
        return td
    
    #指定チームの情報送信
    async def post_teamdata(self, leaderid:str, postdata:dict, apptype:int) -> requests.Response:
        r = await self.db.post_db(name='write', data=postdata, table='team-master', column='リーダー', record=str(leaderid), apptype=apptype)
        return r
    
    #指定チームの情報送信をログ
    def log_teamdata(self, author:discord.User, postdata:dict, currenttime:str, apptype:int) -> requests.Response:
        datekey = ["登録日時", "最終更新日時"]
        for k in datekey:
            if k in postdata: del postdata[k]

        add = {"タイムスタンプ":currenttime, "申請区分":apptype, "実行者Discord名": str(author), "実行者DiscordID": str(author.id)}
        logdata = postdata|add
        r = self.db.post_db(name='log', data=logdata, table='team-log')
        return r