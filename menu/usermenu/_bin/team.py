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
import menufunc

class UserMenu_Team(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.teamfunc = TeamFunc()

    #Slash: チーム情報登録・更新フォームURLを発行するコマンド(リーダーのみ)
    @app_commands.command(name="apply_team")
    async def apply_teaminfo(self, interaction:discord.Interaction, apptype:int, leader:discord.User, member1:discord.User, member2:discord.User, member3:discord.User, member4:discord.User=None) -> None:
        await interaction.response.defer(thinking=True)
        author = interaction.user
        #【チーム情報確認処理】
        teamdata = self.teamfunc.check_leader(author)
        #申請区分が「登録」且つ既にチーム情報が存在する場合
        if apptype == 0 and len(teamdata) != 0:
            await interaction.followup.send()
            return
        #申請区分が「更新」且つチーム情報が存在しない場合
        elif apptype == 1 and len(teamdata) == 0:
            await interaction.followup.send()
            return

        #【ユーザ情報確認処理】
        members = [leader, member1, member2, member3, member4]
        for member in members:
            if member != None:
                userdata = self.teamfunc.check_userdata(member)
                if len(userdata) == 0:
                    await interaction.followup.send()
                    return

        #【チーム情報登録・更新フォームURL生成】
        formurl = self.teamfunc.create_teamformurl(author, teamdata, members)
        await interaction.followup.send(formurl)

    #Slash: チームの平均XPを確認するコマンド(リーダーのみ)
    @app_commands.command(name="average_xp")
    async def get_average_xp(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        r = database.Database().get_db(name='get_team_xp',leaderid=interaction.user.id)
        xps = r.json()
        xpavg = self.teamfunc.cal_average_xp(xps)
        await interaction.followup.send(xpavg)

    ##【コマンド構想】##
    #Slash: チーム情報をアーカイブ化かするコマンド(リーダーのみ)

class TeamFunc():
    def __init__(self):
        pass

    #チームの平均XP計算
    def cal_average_xp(xps:list) -> int:
        f = 50
        xpsr = [int(xp/f)*f for xp in xps]
        xpavg = int(sum(xpsr)/len(xpsr))
        return xpavg

    #コマンド実行者がリーダーか判断
    def check_leader(author:discord.User) -> list:
        r = database.Database().get_db(name='read', arg1='team', arg2=str(author.id))
        td = r.json()
        if td == None: return list()
        else: return td

    #指定ユーザのデータ確認
    def check_userdata(member:discord.User) -> list:
        r = database.Database().get_db(name='read', arg1='indiv', arg2=str(member.id))
        ud = r.json()
        if ud == None: return list()
        else: return ud

    #チーム情報登録・更新フォームURLの生成
    def create_teamformurl(apptype:int, author:discord.User, teamdata:list, members:list) -> str:
        r = database.Database().get_db(name='get_formid', arg1='team', arg2=apptype, arg3=str(author), arg4=str(author.id))
        formid = int(r.text)

        formdata = open_json('team_formdata.json')
        baseids = list(formdata['form']['field']['base'].values())
        basevals = [formid, apptype, str(author), str(author.id)]
        memberdata = sum([[str(member), str(member.id)] for member in members if member!=None],list())
        basevals.extend(memberdata)

        if apptype == 1:
            updateids = list(formdata['form']['field']['update'].values())
            updatevals = database.CommonFunc().teamdata_onlyForUpdate(teamdata)
            formurl = menufunc.create_formurl(apptype,formdata,baseids,basevals,updateids,updatevals)
        elif apptype == 0:
            formurl = menufunc.create_formurl(apptype,formdata,baseids,basevals)

        return formurl


async def setup(client: commands.Bot):
    await client.add_cog(UserMenu_Team(client))

    