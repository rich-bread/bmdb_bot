import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands
from cmmod.json_module import open_json
import cmmod.discord_module
from usermenu.cmfunc.usermenufunc import get_currenttime
from usermenu.cmfunc.userfunc import check_userdata
from usermenu.cmfunc.teamfunc import check_leader, apply_teamdata

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/apply_team.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]
cmddesb = cmddata["describe"]
cmdcho = cmddata["choices"]
cmdcho_apt = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdcho["apptype"]]
cmdcho_lgid = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdcho["leagueid"]]
cmddix = cmddata["dataindex"]

class ApplyTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()
    
    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.describe(apptype=cmddesb["apptype"],teamname=cmddesb["teamname"],league=cmddesb["leagueid"],
    leader=cmddesb["leaderid"],member1=cmddesb["member1id"],member2=cmddesb["member2id"],member3=cmddesb["member3id"],member4=cmddesb["member4id"])
    @app_commands.choices(apptype=cmdcho_apt,league=cmdcho_lgid)
    async def apply_team_command(self, interaction:discord.Interaction, apptype:app_commands.Choice[int], teamname:str, league:app_commands.Choice[int],
    leader:discord.User, member1:discord.User, member2:discord.User, member3:discord.User, member4:discord.User=None) -> None:
        try:
            await interaction.response.defer(thinking=True)

            author = interaction.user #コマンド実行者

            #【チーム情報確認処理】
            teamdata = check_leader(author)
            #[ERROR] 申請区分が「登録」且つ既にチーム情報が存在する場合
            if apptype.value == 0 and len(teamdata) != 0:
                error = "既にいずれかのチームのリーダーとなっています。新たにチーム登録する場合は, 情報更新でリーダーを変更後行ってください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return
            #[ERROR] 申請区分が「更新」且つチーム情報が存在しない場合
            elif apptype.value == 1 and len(teamdata) == 0:
                error = "いずれかのチームのリーダーであることが確認できませんでした。チームリーダーであるにもかかわらず、このエラーメッセージが送信された場合は運営まで連絡してください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【無変更確認処理】
            NCP = 0 #無変更パラメータ
            necs = [teamname, league.value] #情報登録・更新に必要な要素リスト
            necstr = [str(a) for a in necs] #必要リストをstr変換
            #[ERROR] チーム情報がない場合且つ情報更新をしない場合
            if apptype.value == 0 and str(NCP) in necstr:
                error = f"コマンド実行者がリーダーとして登録されているチームの情報を確認できませんでした。未登録の状態で無変更オプション「0」を使うことはできません"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【ユーザ情報確認処理】
            members = [leader, member1, member2, member3, member4]
            for member in members:
                if member != None:
                    userdata = check_userdata(member)
                    #[ERROR] 指定ユーザの情報がデータベースに登録されていない場合
                    if len(userdata) == 0:
                        error = f"指定ユーザ{member.mention}の情報がデータベースに登録されていません。ユーザ情報を登録行ってからチーム情報登録・更新を行ってください"
                        await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                        return
                    #[ERROR] 指定ユーザの情報にウデマエ画像がない場合
                    usercmddata = open_json(r'menu/usermenu/data/apply_user.json') #ユーザ情報申請時に使用するapp_commands用JSON
                    userddix = usercmddata["dataindex"] #ユーザ情報のindex
                    if userdata[userddix["image1"]] == '':
                        error = f"指定ユーザ{member.mention}のウデマエ画像が登録されていません。ウデマエ確認機能追加の為、ウデマエ画像を添付する必要があります。再度画像を添付してから情報更新を行ってください"
                        await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                        return

            #【チーム名確定処理】
            if teamname == str(NCP): TEAMNAME = teamdata[1]
            else: TEAMNAME = teamname

            #【リーグ確定処理】
            if league.value == NCP: LEAGUEID = teamdata[3]
            else: LEAGUEID = league.name

            #【メンバー確定処理】
            LEADERID = str(leader.id)
            MEMBER1ID = str(member1.id)
            MEMBER2ID = str(member2.id)
            MEMBER3ID = str(member3.id)
            #【メンバー4確定処理】5人目のメンバーの指定可否で値を変更
            if member4 != None: MEMBER4ID = str(member4.id)
            elif member4 == None: MEMBER4ID = ''

            #【登録日時確定処理】
            ct = get_currenttime()
            if apptype.value == 0:
                REGISTRATION_DATE = ct
                UPDATE_DATE = ct
            elif apptype.value == 1:
                REGISTRATION_DATE = teamdata[9]
                UPDATE_DATE = ct

            #【チーム情報作成処理】
            TEAMDATA = {"チーム名":TEAMNAME, "リーグID":LEAGUEID, "リーダーID":LEADERID, "メンバー1ID":MEMBER1ID, "メンバー2ID":MEMBER2ID, "メンバー3ID":MEMBER3ID, "メンバー4ID":MEMBER4ID,
            "登録日時":REGISTRATION_DATE, "最終更新日時":UPDATE_DATE}

            #【チーム情報送信処理】
            apply_teamdata(author,leader,apptype.value,TEAMDATA)

        except Exception as e:
            error = "チーム情報登録・更新コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"
            print(error+e)
            await interaction.followup.send(content=author.mention,embed=self.custembed.error(error+e))

        else:
            #【完了送信処理】
            success = f"{author.mention}からリーダー:{leader.mention}のチーム情報{apptype.name}を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))


async def setup(client: commands.Bot):
    await client.add_cog(ApplyTeam(client))
    