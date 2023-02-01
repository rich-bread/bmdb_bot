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
from usermenu.cmfunc.userfunc import check_userdata
from usermenu.cmfunc.teamfunc import check_leader
from usermenu.cmfunc.entryfunc import check_season, apply_entrylog

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/entry_season.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class EntrySeason(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    async def entry_season_command(self, interaction:discord.Interaction):
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者
            #【チーム情報確認処理】
            teamdata = check_leader(author)
            #[ERROR] コマンド実行者がリーダーのチームの情報が存在しない場合
            if len(teamdata) == 0:
                error = "いずれかのチームのリーダーであることが確認できませんでした。参加申請を行う為には、コマンド実行者がリーダーとして登録されているチームの情報が必要です。チーム情報登録後、再度参加申請を行ってください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return
            
            #【ユーザ情報確認処理】
            #teamcmddata = open_json(r'menu/usermenu/data/apply_team.json') #チーム情報申請時に使用するapp_commands用JSON
            #teamddix = teamcmddata["dataindex"] #ユーザ情報のindex
            #usercmddata = open_json(r'menu/usermenu/data/apply_user.json') #ユーザ情報申請時に使用するapp_commands用JSON
            #userddix = usercmddata["dataindex"] #ユーザ情報のindex
            #members = [teamdata[teamddix["leaderid"]],teamdata[teamddix["member1id"]],teamdata[teamddix["member2id"]],teamdata[teamddix["member3id"]],teamdata[teamddix["member4id"]]]
            #for mid in members:
                #if mid != None:
                    #member = await self.client.fetch_user(int(mid))
                    #userdata = check_userdata(member)
                    #[ERROR] 指定ユーザの情報にウデマエ画像がない場合        
                    #if userdata[userddix["image1"]] == '':
                        #error = f"指定ユーザ{member.mention}のウデマエ画像が登録されていません。ウデマエ確認機能追加の為、ウデマエ画像を提出する必要があります"
                        #await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                        #return

            #【シーズン情報確認処理】
            seasondata = check_season() #-> [継続新規判別値,[シーズン情報]]
            #[ERROR] 受付中のシーズンが存在しない場合
            if len(seasondata) == 0:
                error = "現在参加申請を行えるシーズンがありません。受付期間が開始し次第、参加申請を行ってください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【継続新規受付確認処理】
            entryparam = seasondata[0] #継続新規判別値
            regd_seasonid = teamdata[2] #チーム情報に登録されているリーグID
            #[ERROR] 継続受付且つチーム情報にリーグIDが登録されていない場合
            if entryparam == 0 and regd_seasonid == '':
                error = "過去に参加したシーズンを確認できませんでした。継続受付を行う為には、コマンド実行者がリーダーとして登録されているチームが過去にシーズンに参加をした記録が必要です。新規受付期間開始をお待ちください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return
            
            #【参加申請情報値確定処理】
            SEASONDATA = seasondata[1] #シーズン情報
            SEASONNAME = SEASONDATA[1] #シーズン名
            SEASONID = SEASONDATA[2] #シーズンID
            TEAMNAME = teamdata[1] #チーム名

            UPDATE_TIME = get_currenttime()
            
            #【参加申請情報作成処理】
            ENTRYLOG = {"シーズン名": SEASONNAME, "シーズンID": SEASONID, "チーム名": TEAMNAME}

            #【参加申請情報送信処理】
            apply_entrylog(author=author, entryparam=entryparam, timestamp=UPDATE_TIME, entrylog=ENTRYLOG)
        
        except Exception as e:
            error = "参加申請コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"
            print(error+e)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error+e))

        else:
            #【完了送信処理】
            success = f"{author.mention}からシーズン:`{SEASONNAME}`への参加申請を受け付けました。データベースからの参加受付通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))

async def setup(client: commands.Bot):
    await client.add_cog(EntrySeason(client))
