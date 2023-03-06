import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands
from cmmod.json_module import open_json
from cmmod.discord_module import CustomEmbed
from usermenu.cmfunc.userfunc import UserDBFunc
from usermenu.cmfunc.teamfunc import TeamFunc, TeamDBFunc

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/check_team.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class CheckTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.userdbfunc = UserDBFunc()
        self.teamfunc = TeamFunc()
        self.teamdbfunc = TeamDBFunc()
        self.custembed = CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.guild_only()
    async def check_team_command(self, interaction:discord.Interaction):
        author = interaction.user #コマンド実行者
        try:
            #【thinking処理】
            await interaction.response.defer(ephemeral=True, thinking=True)

            #【チーム情報確認処理】
            raw_teamdata = await self.teamdbfunc.get_teamdata(leaderid=author.id)
            teamdata = raw_teamdata[0]
            #[ERROR] チーム情報が存在しない場合
            if not teamdata:
                error = "いずれかのチームのリーダーであることが確認できませんでした。チーム情報登録を行ってから再度実行してください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【平均XP計算処理】
            teamcmddata = open_json(r'menu/usermenu/data/apply_team.json') #ユーザ情報申請時に使用するapp_commands用JSON
            teamcmddix = teamcmddata["dataindex"] #チーム情報のindex

            members = [teamdata[teamcmddix["leader"]],teamdata[teamcmddix["member1"]],teamdata[teamcmddix["member2"]],teamdata[teamcmddix["member3"]],teamdata[teamcmddix["member4"]]]
            xps = []
            for mid in members:
                raw_userdata = await self.userdbfunc.get_userdata(userid=mid)
                userdata = raw_userdata[0]
                if not userdata: continue
                xps.append(userdata[9])
            xpavg = self.teamfunc.cal_averagexp(xps=xps)
            
            #【閲覧用ユーザ情報作成処理】
            viewdata = f"チーム名: {teamdata[teamcmddix['teamname']]}\n"+\
                        f"リーグ: {teamdata[teamcmddix['league']]}\n"+\
                        f"平均XP: {xpavg}\n"+\
                        f"リーダー: <@{teamdata[teamcmddix['leader']]}>\n"+\
                        f"メンバー①: <@{teamdata[teamcmddix['member1']]}>\n"+\
                        f"メンバー②: <@{teamdata[teamcmddix['member2']]}>\n"+\
                        f"メンバー③: <@{teamdata[teamcmddix['member3']]}>\n"
            if teamdata[teamcmddix['member4']] != '': viewdata+"\nメンバー④: <@"+teamdata[teamcmddix['member4']]+">"

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))

        else:
            #【完了送信処理】
            title = f"{teamdata[teamcmddix['teamname']]}のチーム情報"
            await interaction.followup.send(content=author.mention, embed=self.custembed.default(title=title,description=viewdata))
        

async def setup(client: commands.Bot):
    await client.add_cog(CheckTeam(client))
    