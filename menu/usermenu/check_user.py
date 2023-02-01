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
from usermenu.cmfunc.userfunc import check_userdata
from usermenu.cmfunc.teamfunc import check_leader

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/check_user.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]
cmddesb = cmddata["describe"]

class CheckUser(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()

    @app_commands.command(name=cmdname,description=cmddesp)
    @app_commands.describe(user=cmddesb["user"])
    async def check_user_command(self, interaction:discord.Interaction, user:discord.User):
        try:
            await interaction.response.defer(ephemeral=True,thinking=True)

            author = interaction.user #コマンド実行者
            #【ユーザ情報確認処理】
            userdata = check_userdata(user)
            #[ERROR] 指定ユーザの情報が存在しない場合
            if len(userdata) == 0:
                error = f"指定ユーザ{user.mention}の情報がデータベースに登録されていません。ユーザ情報登録を行ってから再度実行してください"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【ユーザ情報閲覧資格確認処理】他ユーザ指定時 ※指定ユーザとコマンド実行者が同じ場合はskip
            if author != user:
                teamdata = check_leader(author)
                #[ERROR] リーダーではない場合
                if len(teamdata) == 0:
                    error = "いずれかのチームのリーダーであることが確認できませんでした。本人以外のユーザ情報を確認する場合は指定ユーザが所属するチームのリーダーである必要があります"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return

                teamcmddata = open_json(r'menu/usermenu/data/apply_team.json') #チーム情報申請時に使用するapp_commands用JSON
                teamcmddix = teamcmddata["dataindex"] #チーム情報のindex
                matchids = [teamdata[i] for i in list(range(teamcmddix["member1id"], teamcmddix["member4id"]+1)) if teamdata[i] == str(user.id)] #チームに所属するメンバーのDiscordIDと比較/該当IDをリストに追加
                #[ERROR] 指定ユーザがリーダーのチームに所属していない場合
                if len(matchids) != 1:
                    error = f"指定ユーザ{user.mention}はリーダー{author.mention}のチームに所属していません。本人以外のユーザ情報を閲覧する場合は指定ユーザが所属するチームのリーダーである必要があります"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return

            #【閲覧用ユーザ情報作成処理】
            usercmddata = open_json(r'menu/usermenu/data/apply_user.json') #ユーザ情報申請時に使用するapp_commands用JSON
            usercmddix = usercmddata["dataindex"] #ユーザ情報のindex
            USERDATA =  f"名前:{userdata[usercmddix['name']]}\n"+\
                        f"フレンドコード:{userdata[usercmddix['friendcode']]}\n"+\
                        f"TwitterID:{userdata[usercmddix['twitterid']]}\n"+\
                        f"ポジション:{userdata[usercmddix['position']]}\n"+\
                        f"持ちブキ:{userdata[usercmddix['buki']]}\n"+\
                        f"最高XP(エリア):{userdata[usercmddix['splatzone_xp']]}\n"+\
                        f"最高XP(全ルール):{userdata[usercmddix['allmode_xp']]}"

        except Exception as e:
            error = "ユーザ情報閲覧コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"
            print(error+e)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error+e))

        else:
            #【完了送信処理】
            title = f"{str(user)}のユーザ情報"
            await interaction.followup.send(content=author.mention, embed=self.custembed.default(title=title,description=USERDATA))


async def setup(client: commands.Bot):
    await client.add_cog(CheckUser(client))
