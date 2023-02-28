import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands
from cmmod.json_module import open_json
from cmmod.time_module import get_currenttime
from cmmod.discord_module import CustomEmbed
from usermenu.cmfunc.userfunc import UserDBFunc
from usermenu.cmfunc.teamfunc import TeamDBFunc
from usermenu.error.usermenu_error import UserMenuError

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/apply_team.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]
cmddesb = cmddata["describe"]
cmdcho = cmddata["choices"]
cmdcho_apt = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdcho["apptype"]]
cmdcho_lgid = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdcho["league"]]
cmddix = cmddata["dataindex"]

class ApplyTeam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.userdbfunc = UserDBFunc()
        self.teamdbfunc = TeamDBFunc()
        self.custembed = CustomEmbed()
    
    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.describe(apptype=cmddesb["apptype"],teamname=cmddesb["teamname"],league=cmddesb["league"],
    leader=cmddesb["leader"],member1=cmddesb["member1"],member2=cmddesb["member2"],member3=cmddesb["member3"],member4=cmddesb["member4"])
    @app_commands.choices(apptype=cmdcho_apt,league=cmdcho_lgid)
    @app_commands.guild_only()
    async def apply_team_command(self, interaction:discord.Interaction, apptype:app_commands.Choice[int], teamname:str, league:app_commands.Choice[int],
    leader:discord.User, member1:discord.User, member2:discord.User, member3:discord.User, member4:discord.User=None) -> None:
        author = interaction.user #コマンド実行者
        try:
            #【thinking処理】
            await interaction.response.defer(thinking=True)

            #【チーム情報確認処理】
            raw_teamdata = await self.teamdbfunc.get_teamdata(leaderid=author.id)
            teamdata = raw_teamdata[0]
            #[ERROR] 申請区分が「登録」且つ既にチーム情報が存在する場合
            if apptype.value == 0 and teamdata:
                error = "既にいずれかのチームのリーダーとなっています。新たにチーム登録する場合は、情報更新でリーダーを変更後行ってください"
                raise UserMenuError(error)
            #[ERROR] 申請区分が「更新」且つチーム情報が存在しない場合
            elif apptype.value == 1 and not teamdata:
                error = "いずれかのチームのリーダーであることが確認できませんでした。チームリーダーであるにもかかわらず、このエラーメッセージが送信された場合は運営まで連絡してください"
                raise UserMenuError(error)

            #【ユーザ情報確認処理】
            members = [leader, member1, member2, member3, member4]
            for member in members:
                if member != None:
                    raw_userdata = await self.userdbfunc.get_userdata(member.id)
                    userdata = raw_userdata[0]
                    #[ERROR] 指定ユーザの情報がデータベースに登録されていない場合
                    if not userdata:
                        error = f"指定ユーザ{member.mention}の情報がデータベースに登録されていません。ユーザ情報を登録行ってからチーム情報登録・更新を行ってください"
                        raise UserMenuError(error)
                    
            #【メンバー4確定処理】
            if member4 == None: MEMBER4 = ''
            else: MEMBER4 = str(member4.id)

            #【登録日時確定処理】
            currenttime = get_currenttime()
            if apptype.value == 0: REGISTRATION_DATE = currenttime
            else: REGISTRATION_DATE = teamdata[9]

            #【チーム情報作成処理】
            postdata = {"チーム名":teamname, "リーグ":league.name, "リーダー":str(leader.id), "メンバー1":str(member1.id), "メンバー2":str(member2.id), 
                        "メンバー3":str(member3.id), "メンバー4":MEMBER4, "登録日時":REGISTRATION_DATE, "最終更新日時":currenttime}

            #【POST処理】
            await self.teamdbfunc.post_teamdata(leaderid=leader.id, postdata=postdata, apptype=apptype.value)
            await self.teamdbfunc.log_teamdata(author=author, postdata=postdata, currenttime=currenttime, apptype=apptype.value)

        except UserMenuError as e:
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(description=str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention,embed=self.custembed.error(description=error))

        else:
            #【完了送信処理】
            success = f"{author.mention}からリーダー:{leader.mention}のチーム情報{apptype.name}を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(description=success))


async def setup(client: commands.Bot):
    await client.add_cog(ApplyTeam(client))
    