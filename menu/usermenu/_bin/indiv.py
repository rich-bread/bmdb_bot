import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands
import database
from cmmod.json_module import open_json
from menufunc import create_formurl

class UserMenu_Indiv(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.indivfunc = IndivFunc()

    #Slash: ユーザ情報登録・更新フォームURLを発行するコマンド
    @app_commands.command(name='apply_user')
    async def apply_user(self, interaction:discord.Interaction, user:discord.User, image1:discord.Attachment, image2:discord.Attachment=None) -> None:
        await interaction.response.defer(thinking=True)
        author = interaction.user #コマンド実行者
        #【ユーザ情報確認処理】
        userdata = self.indivfunc.check_userdata(user)
        if len(userdata) == 0: apptype = 0
        elif len(userdata) != 0: apptype = 1
        else: 
            return

        #【ユーザ情報登録・更新フォームURL生成】
        formurl = self.indivfunc.create_indivformurl(apptype,author,user,userdata)
        await interaction.followup.send(formurl)

    #Slash: DBに登録されているユーザ情報を確認するコマンド(本人のみ)
    @app_commands.command(name='check_user')
    async def check_user(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        author = interaction.user #コマンド実行者
        #【ユーザ情報確認処理】
        userdata = self.indivfunc.check_userdata(author)
        if len(userdata) == 0:
            await interaction.followup.send() #未登録の場合
            return
        

class IndivFunc():
    def __init__(self):
        pass

    #指定ユーザのデータ確認
    def check_userdata(self, user:discord.User) -> list:
        r = database.Database().get_db(name='read', arg1='indiv', arg2=str(user.id))
        ud = r.json()
        if ud == None: return list()
        else: return ud

    #ユーザ情報登録・更新フォームURLの生成
    def create_indivformurl(self, apptype:int, author:discord.User, user:discord.User, userdata:list) -> str:
        r = database.Database().get_db(name='get_formid', arg1='indiv', arg2=apptype, arg3=str(author), arg4=str(author.id), arg5=str(user), arg6=str(user.id))
        formid = int(r.text)

        formdata = open_json('./data/indiv_formdata.json')
        baseids = list(formdata['form']['field']['base'].values())
        basevals = [formid, apptype, str(author), str(author.id), str(user), str(user.id)]

        if apptype == 1:
            updateids = list(formdata['form']['field']['update'].values())
            updatevals = database.CommonFunc().userdata_onlyForUpdate(userdata)
            formurl = create_formurl(apptype,formdata,baseids,basevals,updateids,updatevals)
        elif apptype == 0:
            formurl = create_formurl(apptype,formdata,baseids,basevals)

        return formurl

async def setup(client: commands.Bot):
    await client.add_cog(UserMenu_Indiv(client))
