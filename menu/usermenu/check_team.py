import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands
import cmmod.discord_module
from cmmod.json_module import open_json
from usermenu.cmfunc.teamfunc import check_leader

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/check_team.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class CheckTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    async def check_team_command(self, interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        author = interaction.user #コマンド実行者

        #【チーム情報確認処理】
        teamdata = check_leader(author)
        #[ERROR] チーム情報が存在しない場合
        if len(teamdata) == 0:
            error = "いずれかのチームのリーダーであることが確認できませんでした。チーム情報登録を行ってから再度実行してください"
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
            return

        #【閲覧用ユーザ情報作成処理】
        teamcmddata = open_json(r'menu/usermenu/data/apply_team.json') #ユーザ情報申請時に使用するapp_commands用JSON
        teamcmddix = teamcmddata["dataindex"] #ユーザ情報のindex
        if teamdata[teamcmddix['member4id']] == '': MEMBER4ID = ''
        else: MEMBER4ID = "<@"+teamdata[teamcmddix['member4id']]+">"

        TEAMDATA =  f"チーム名:{teamdata[teamcmddix['teamname']]}\n"+\
                    f"リーグ:{teamdata[teamcmddix['leagueid']]}\n"+\
                    f"リーダー:<@{teamdata[teamcmddix['leaderid']]}>\n"+\
                    f"メンバー①:<@{teamdata[teamcmddix['member1id']]}>\n"+\
                    f"メンバー②:<@{teamdata[teamcmddix['member2id']]}>\n"+\
                    f"メンバー③:<@{teamdata[teamcmddix['member3id']]}>\n"+\
                    f"メンバー④:{MEMBER4ID}"

        #【完了送信処理】
        title = f"{teamdata[teamcmddix['teamname']]}のチーム情報"
        await interaction.followup.send(content=author.mention, embed=self.custembed.default(title=title,description=TEAMDATA))

async def setup(client: commands.Bot):
    await client.add_cog(CheckTeam(client))
