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
from usermenu.cmfunc.teamfunc import check_leader, get_teamxps, cal_averagexp

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/get_averagexp.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class AverageXP(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()
    
    #Slash: チームの平均XPを確認するコマンド(リーダーのみ)
    @app_commands.command(name=cmdname,description=cmddesp)
    async def get_averagexp_command(self, interaction:discord.Interaction) -> None:
        try:
            await interaction.response.defer(ephemeral=True,thinking=True)

            author = interaction.user #コマンド実行者

            teamdata = check_leader(author)
            #[ERROR] コマンド実行者がリーダーのチーム情報が存在しない場合
            if len(teamdata) == 0:
                error = "コマンド実行者がリーダーとして登録されているチーム情報を確認できませんでした。チーム平均XPを確認するためには、登録されているチーム情報が必要です"
                await interaction.followup.send(content=author.mention,embed=self.custembed.error(error))
                return

            xps = get_teamxps(author) #チームメンバーのXP
            #[ERROR] XPのレスポンスがNoneだった場合 ※ありえないけど一応
            if xps == None:
                error = "チームに登録されているユーザの情報が確認できませんでした。ユーザ情報登録を行ってから、このコマンドを実行してください"
                await interaction.followup.send(content=author.mention,embed=self.custembed.error(error))
                return
            xpavg = cal_averagexp(xps) #チーム平均XPを計算

        except Exception as e:
            error = "チーム平均XPコマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"
            print(error+e)
            await interaction.followup.send(content=author.mention,embed=self.custembed.error(error+e))
            
        else:
            title = f"{str(author)}のチーム"
            success = f"平均XP: {xpavg}"
            await interaction.followup.send(content=author.mention,embed=self.custembed.default(title=title, description=success))
    
async def setup(client: commands.Bot):
    await client.add_cog(AverageXP(client))
    