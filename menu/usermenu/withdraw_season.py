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
from usermenu.cmfunc.usermenufunc import get_currenttime
from usermenu.cmfunc.teamfunc import check_leader
from usermenu.cmfunc.entryfunc import check_season, apply_entrylog

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/withdraw_season.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class WithdrawSeason(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.guild_only()
    async def abstain_season_command(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        author = interaction.user #コマンド実行者

        #【チーム情報確認処理】
        teamdata = check_leader(author)
        #[ERROR] コマンド実行者がリーダーのチームの情報が存在しない場合
        if len(teamdata) == 0:
            error = "いずれかのチームのリーダーであることが確認できませんでした。棄権申請を行う為には、コマンド実行者がリーダーとして登録されているチームの情報が必要です。チーム情報登録後、再度参加申請を行ってください"
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
            return
        #[ERROR] チーム情報にシーズンIDがない場合
        if teamdata[2] == '':
            error = "コマンド実行者がリーダーとして登録されているチームがシーズンに参加した記録がない為、棄権申請を行うことができません"
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
            return

        #【シーズン情報確認処理】
        seasondata = check_season() #-> [継続新規判別値,[シーズン情報]]
        #[ERROR] 受付中のシーズンが存在しない場合
        if len(seasondata) == 0:
            error = "現在受付期間中のシーズンがありません。受付期間を過ぎてから棄権申請を行う場合は、運営へお問い合わせください"
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
            return

        #【参加申請情報値確定処理】
        ENTRYPARAM = 2 #棄権受付区分
        SEASONDATA = seasondata[1] #シーズン情報
        SEASONNAME = SEASONDATA[1]+"【棄権】" #シーズン名
        SEASONID = "BML3WDS" #シーズンID
        TEAMNAME = teamdata[1] #チーム名

        UPDATE_TIME = get_currenttime()
        
        #【参加申請情報作成処理】
        ENTRYLOG = {"シーズン名": SEASONNAME, "シーズンID": SEASONID, "チーム名": TEAMNAME}

        #【参加申請情報送信処理】
        apply_entrylog(author=author, entryparam=ENTRYPARAM, timestamp=UPDATE_TIME, entrylog=ENTRYLOG)

        #【完了送信処理】
        success = f"{author.mention}からシーズン:`{SEASONNAME}`への棄権申請を受け付けました。データベースからの棄権受付通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
        await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))

async def setup(client: commands.Bot):
    await client.add_cog(WithdrawSeason(client))
