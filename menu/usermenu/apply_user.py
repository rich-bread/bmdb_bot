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
from usermenu.cmfunc.userfunc import check_userdata, check_friendcode, check_twitterid, apply_userdata

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/apply_user.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]
cmddesb = cmddata["describe"]
cmdcho = cmddata["choices"]
cmdcho_pos = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdcho["position"]]
cmdcho_buki = [app_commands.Choice(name=c["name"],value=c["value"]) for c in cmdcho["buki"]]
cmddix = cmddata["dataindex"]

class ApplyUser(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()

    #Slash: ユーザ情報登録・更新コマンド
    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.describe(user=cmddesb["user"],name=cmddesb["name"],friendcode=cmddesb["friendcode"],twitterid=cmddesb["twitterid"],position=cmddesb["position"],
    buki=cmddesb["buki"],splatzone_xp=cmddesb["splatzone_xp"],allmode_xp=cmddesb["allmode_xp"],image1=cmddesb["image1"],image2=cmddesb["image2"])
    @app_commands.choices(position=cmdcho_pos,buki=cmdcho_buki)
    @app_commands.guild_only()
    async def apply_user_command(self, interaction:discord.Interaction, user:discord.User, name:str, friendcode:str, twitterid:str, 
    position:app_commands.Choice[int], buki:app_commands.Choice[int], splatzone_xp:int, allmode_xp:int, 
    image1:discord.Attachment=None, image2:discord.Attachment=None) -> None:
        await interaction.response.defer(thinking=True)

        try:
            author = interaction.user #コマンド実行者
            #【ユーザ情報確認処理】
            userdata = check_userdata(user)
            if len(userdata) == 0: 
                apptype = 0
                apptype_str = "登録"
            elif len(userdata) != 0: 
                apptype = 1
                apptype_str = "更新"
            else: return    

            #【無変更確認処理】
            NCP = 0 #無変更パラメータ
            necs = [name, friendcode, twitterid, position.value, buki.value, splatzone_xp, allmode_xp] #情報登録・更新に必要な要素リスト
            necstr = [str(a) for a in necs] #必要リストをstr変換
            #[ERROR] ユーザ情報がない場合且つ情報更新をしない場合
            if apptype == 0 and str(NCP) in necstr:
                error = f"指定ユーザ{user.mention}のユーザ情報を確認できませんでした。未登録の状態で無変更オプション「0」を使うことはできません"
                await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                return

            #【画像添付確認処理】
            #[ERROR] ユーザ情報登録時にウデマエ画像が添付されていない場合
            if apptype == 0: 
                if image1 == None:
                    error = "ユーザ情報登録時にはウデマエ画像を添付する必要があります。再度画像を添付してから情報登録を行ってください"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return
            #[ERROR] DBから取得したウデマエ画像1に何も記入されていなかった場合 ※旧ver時に登録したユーザ用
            if apptype == 1:
                if userdata[cmddix["image1"]] == '' and image1 == None:
                    error = "ウデマエ確認機能追加の為、ウデマエ画像を添付する必要があります。再度画像を添付してから情報更新を行ってください"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return
            #[ERROR] 最高XPを変更する場合且つ画像添付がない場合
            if splatzone_xp != NCP or allmode_xp != NCP:
                if image1 == None:
                    error = "最高XPを変更する場合は、ウデマエ画像を添付する必要があります。再度画像を添付してから情報更新を行ってください"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return

            #【名前確定処理】
            if name == str(NCP): NAME = userdata[cmddix["name"]]
            else: NAME = name

            #【フレンドコード確定処理】
            if friendcode == str(NCP): FRIENDCODE = userdata[cmddix["friendcode"]]
            else:
                cfc = check_friendcode(friendcode)
                #[ERROR] 指定のフレンドコード入力規則に合致しない場合
                if cfc != True: 
                    error = "入力されたフレンドコードが指定の入力規則に合致しませんでした。ハイフンを含めて半角数字12桁でフレンドコードを入力してください"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return
                else:
                    FRIENDCODE = friendcode

            #【TwitterID確定処理】
            if twitterid == str(NCP): TWITTERID = userdata[cmddix["twitterid"]]
            else:
                cti = check_twitterid(twitterid)
                #[ERROR] 正しいTwitterIDの入力がされなかった場合
                if cti != True: 
                    error = "正しいTwitterIDではありません。@を含めて半角英数字でTwitterIDを入力してください"
                    await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))
                    return
                else: TWITTERID = twitterid

            #【ポジション確定処理】
            if position.value == NCP: POSITION = userdata[cmddix["position"]]
            else: POSITION = position.name

            #【持ちブキ確定処理】
            if buki.value == NCP: BUKI = userdata[cmddix["buki"]]
            else: BUKI = buki.name

            #【最高XP(エリア)確定処理】
            if splatzone_xp == NCP: SPLATZONE_XP = userdata[cmddix["splatzone_xp"]]
            else: SPLATZONE_XP = splatzone_xp

            #【最高XP(全ルール)確定処理】
            if allmode_xp == NCP: ALLMODE_XP = userdata[cmddix["allmode_xp"]]
            else: ALLMODE_XP = allmode_xp

            #【ウデマエ画像1確定処理】
            if image1 == None: 
                if apptype == 0: IMAGE1 = ''
                elif apptype == 1: IMAGE1 = userdata[cmddix["image1"]]
            else: IMAGE1 = image1.url

            #【ウデマエ画像2確定処理】
            if image2 == None: 
                if apptype == 0: IMAGE2 = ''
                elif apptype == 1: IMAGE2 = userdata[cmddix["image2"]]
            else: IMAGE2 = image2.url

            #【登録日時確定処理】
            ct = get_currenttime()
            if apptype == 0:
                REGISTRATION_DATE = ct
                UPDATE_DATE = ct
            elif apptype == 1:
                REGISTRATION_DATE = str(userdata[cmddix["registration_date"]])
                UPDATE_DATE = ct

            #【ユーザ情報作成処理】
            USERDATA = {"名前":NAME, "フレンドコード":FRIENDCODE, "TwitterID":TWITTERID, "Discord名":str(user), "DiscordID":str(user.id),
                "ポジション":POSITION, "持ちブキ":BUKI, "最高XP(エリア)":SPLATZONE_XP, "最高XP(全ルール)":ALLMODE_XP, "ウデマエ画像1":IMAGE1, "ウデマエ画像2":IMAGE2,
                "登録日時":REGISTRATION_DATE, "最終更新日時":UPDATE_DATE}

            #【ユーザ情報送信処理】
            apply_userdata(author, user, apptype, USERDATA)

            #【完了送信処理】
            success = f"{author.mention}から{user.mention}のユーザ情報{apptype_str}を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))

        except Exception as e:
            error = "ユーザ情報登録・更新コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"
            print(error+e)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error+e))


async def setup(client: commands.Bot):
    await client.add_cog(ApplyUser(client))
    