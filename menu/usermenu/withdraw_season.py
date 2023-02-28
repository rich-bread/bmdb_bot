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
from cmmod.time_module import get_currenttime
from usermenu.cmfunc.teamfunc import TeamDBFunc
from usermenu.cmfunc.entryfunc import EntryDBFunc

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/withdraw_season.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class WithdrawSeason(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.teamdbfunc = TeamDBFunc()
        self.entrydbfunc = EntryDBFunc()
        self.custembed = cmmod.discord_module.CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.guild_only()
    async def abstain_season_command(self, interaction:discord.Interaction):
        author = interaction.user #コマンド実行者
        try:
            #【thinking処理】
            await interaction.response.defer(thinking=True)

            #【チーム情報確認処理】
            raw_teamdata = await self.teamdbfunc.get_teamdata(leaderid=author.id)
            teamdata = raw_teamdata[0]
            #[ERROR] コマンド実行者がリーダーのチームの情報が存在しない場合
            if not teamdata:
                error = "いずれかのチームのリーダーであることが確認できませんでした。棄権申請を行う為には、コマンド実行者がリーダーとして登録されているチームの情報が必要です。チーム情報登録後、再度参加申請を行ってください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return
            #[ERROR] チーム情報にシーズンIDがない場合
            if teamdata[2] == '':
                error = "コマンド実行者がリーダーとして登録されているチームがシーズンに参加した記録がない為、棄権申請を行うことができません"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【シーズン情報確認処理】
            seasondata = await self.entrydbfunc.get_seasondata() #シーズン情報
            #[ERROR] 受付中のシーズンが存在しない場合
            if not seasondata:
                error = "現在受付期間中のシーズンがありません。受付期間を過ぎてから棄権申請を行う場合は、運営へお問い合わせください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return
            
            #【棄権申請情報作成処理】
            currenttime = get_currenttime()
            entrydata = {"タイムスタンプ":currenttime, "実行者Discord名":str(author), "実行者DiscordID":str(author.id),
                            "シーズン名":seasondata[1]+"【棄権】", "シーズンID":"BML3WDS", "チーム名":teamdata[1]}

            #【POST処理】
            await self.entrydbfunc.log_entrydata(entrydata)

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"
            print(error+e)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error+str(e)))

        else:
            #【完了送信処理】
            success = f"{author.mention}からシーズン:`{seasondata[1]}`への棄権申請を受け付けました。データベースからの棄権受付通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))

async def setup(client: commands.Bot):
    await client.add_cog(WithdrawSeason(client))
