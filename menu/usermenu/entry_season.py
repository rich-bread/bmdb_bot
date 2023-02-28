import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands

from cmmod.json_module import open_json
from cmmod.time_module import get_currenttime, str_to_datetime
from cmmod.discord_module import CustomEmbed
from usermenu.error.usermenu_error import UserMenuError
from usermenu.cmfunc.userfunc import UserFunc, UserDBFunc
from usermenu.cmfunc.teamfunc import TeamFunc, TeamDBFunc
from usermenu.cmfunc.entryfunc import EntryDBFunc

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/entry_season.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]
cmddix = cmddata["dataindex"]

class EntrySeason(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client
        self.userfunc = UserFunc()
        self.userdbfunc = UserDBFunc()
        self.teamfunc = TeamFunc()
        self.teamdbfunc = TeamDBFunc()
        self.entrydbfunc = EntryDBFunc()
        self.custembed = CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.guild_only()
    async def entry_season_command(self, interaction:discord.Interaction):
        author = interaction.user #コマンド実行者
        try:
            #【thinking処理】
            await interaction.response.defer(thinking=True)

            #【シーズン情報確認処理】
            seasondata = await self.entrydbfunc.get_seasondata()
            #[ERROR] 受付中のシーズンが存在しない場合
            if not seasondata:
                error = "現在参加申請を行えるシーズンがありません。受付期間が開始し次第、参加申請を行ってください"
                raise UserMenuError(error)
            
            #【チーム情報確認処理】
            raw_teamdata = await self.teamdbfunc.get_teamdata(leaderid=author.id)
            teamdata = raw_teamdata[0]
            #[ERROR] コマンド実行者がリーダーのチームの情報が存在しない場合
            if not teamdata:
                error = "いずれかのチームのリーダーであることが確認できませんでした。参加申請を行う為には、コマンド実行者がリーダーとして登録されているチームの情報が必要です。チーム情報登録後、再度参加申請を行ってください"
                raise UserMenuError(error)
            
            #【ユーザ情報確認処理】
            teamcmddata = open_json(r'menu/usermenu/data/apply_team.json') #チーム情報申請時に使用するapp_commands用JSON
            teamddix = teamcmddata["dataindex"] #チーム情報のindex
            usercmddata = open_json(r'menu/usermenu/data/apply_user.json') #ユーザ情報申請時に使用するapp_commands用JSON
            userddix = usercmddata["dataindex"] #ユーザ情報のindex
            members = [teamdata[teamddix["leader"]],teamdata[teamddix["member1"]],teamdata[teamddix["member2"]],teamdata[teamddix["member3"]],teamdata[teamddix["member4"]]]
            for mid in members:
                raw_userdata = await self.userdbfunc.get_userdata(userid=mid)
                userdata = raw_userdata[0]
                if not userdata: continue
                #[ERROR] 指定ユーザの情報にウデマエ画像がない場合
                if userdata[userddix["image1"]] == '':
                    error = f"指定ユーザ:<@{mid}>のウデマエ画像が登録されていません。ウデマエ確認機能追加の為、ウデマエ画像を提出する必要があります"
                    raise UserMenuError(error)
                
                #[ERROR] 指定ユーザの最終更新日時が受付期間よりも前の場合
                userupdate = str_to_datetime(userdata[userddix["update_date"]])
                entrystart = str_to_datetime(seasondata[cmddix["entry_from"]])
                if userupdate < entrystart:
                    error = f"指定ユーザ:<@{mid}>のウデマエ画像更新が確認できませんでした。ウデマエ確認機能追加の為、シーズン毎に最新の最高XP及びウデマエ画像を提出する必要があります ※有効なウデマエ画像についてはルールブックを確認してください"
                    raise UserMenuError(error)
            
            #【チーム情報作成処理】
            currenttime = get_currenttime()
            teampostdata = {"シーズンID":seasondata[cmddix["seasonid"]], "最終更新日時":currenttime}

            #【参加申請情報作成処理】
            entrydata = {"タイムスタンプ":currenttime, "実行者Discord名":str(author), "実行者DiscordID":str(author.id),
                         "シーズン名":seasondata[cmddix["seasonname"]], "シーズンID":seasondata[cmddix["seasonid"]], "チーム名":teamdata[teamddix["teamname"]]}
            
            #【POST処理】
            await self.teamdbfunc.post_teamdata(leaderid=author.id, postdata=teampostdata, apptype=1)
            await self.entrydbfunc.log_entrydata(logdata=entrydata)
        
        except UserMenuError as e:
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(description=str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))

        else:
            #【完了送信処理】
            success = f"{author.mention}からシーズン:`{seasondata[cmddix['seasonname']]}`への参加申請を受け付けました。データベースからの参加受付通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))

async def setup(client: commands.Bot):
    await client.add_cog(EntrySeason(client))
    