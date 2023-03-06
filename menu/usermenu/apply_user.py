import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import discord
from discord.ext import commands
from discord import app_commands
from cmmod.json_module import open_json
from cmmod.discord_module import CustomEmbed
from cmmod.time_module import get_currenttime
from usermenu.cmfunc.userfunc import UserFunc, UserDBFunc
from usermenu.error.usermenu_error import UserMenuError

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
        self.userfunc = UserFunc()
        self.userdbfunc = UserDBFunc()
        self.custembed = CustomEmbed()

    #Slash: ユーザ情報登録・更新コマンド
    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.describe(user=cmddesb["user"],name=cmddesb["name"],friendcode=cmddesb["friendcode"],twitterid=cmddesb["twitterid"],position=cmddesb["position"],
    buki=cmddesb["buki"],splatzone_xp=cmddesb["splatzone_xp"],allmode_xp=cmddesb["allmode_xp"],image1=cmddesb["image1"],image2=cmddesb["image2"])
    @app_commands.choices(position=cmdcho_pos,buki=cmdcho_buki)
    @app_commands.guild_only()
    async def apply_user_command(self, interaction:discord.Interaction, user:discord.User, name:str, friendcode:str, twitterid:str, 
    position:app_commands.Choice[int], buki:app_commands.Choice[int], splatzone_xp:int, allmode_xp:int, 
    image1:discord.Attachment=None, image2:discord.Attachment=None) -> None:
        author = interaction.user #コマンド実行者
        try:
            #【thinking処理】
            await interaction.response.defer(thinking=True)
            
            #【ユーザ情報確認処理】
            raw_userdata = await self.userdbfunc.get_userdata(userid=user.id)
            userdata = raw_userdata[0]
            if not userdata:
                apptype = 0
                apptype_str = "登録"
            else:
                apptype = 1
                apptype_str = "更新"

            #【無変更確認処理】
            NOCHANGEPARAM = 0
            necs = [name, friendcode, twitterid, position.value, buki.value, splatzone_xp, allmode_xp] #情報登録・更新に必要な要素リスト
            #[ERROR] ユーザ情報がない場合且つ情報更新を
            if apptype == 0 and (NOCHANGEPARAM in necs or str(NOCHANGEPARAM) in necs):
                error = f"指定ユーザ{user.mention}のユーザ情報を確認できませんでした。未登録状態で無変更オプション「0」を使うことはできません"
                raise UserMenuError(error)
            
            #【ウデマエ画像確認処理】
            #[ERROR] ユーザ情報登録時にウデマエ画像が添付されていない場合
            if apptype == 0 and image1 == None:
                error = "ユーザ情報登録時にはウデマエ画像を提出する必要があります。再度ウデマエ画像を添付してから情報登録を行ってください"
                raise UserMenuError(error)
            #[ERROR] DBから取得したユーザ情報にウデマエ画像が添付されていない場合 #旧ver時に登録したユーザ用
            if apptype == 1 and userdata[cmddix["image1"]] == '' and image1 == None:
                error = "ウデマエ確認機能追加の為、ウデマエ画像を提出する必要があります。再度ウデマエ画像を添付してから情報更新を行ってください"
                raise UserMenuError(error)
            #[ERROR] 最高XPを変更する場合且つ画像添付がない場合
            if (splatzone_xp != NOCHANGEPARAM or allmode_xp != NOCHANGEPARAM) and image1 == None:
                error = "最高XPを変更する場合は、同時にウデマエ画像を提出する必要があります。再度ウデマエ画像を添付してから情報更新を行ってください"
                raise UserMenuError(error)
            
            #【各入力・選択項目確定処理】
            #【名前確定】
            if name == str(NOCHANGEPARAM): NAME = userdata[cmddix["name"]]
            else: NAME = name
            #【フレンドコード確定】
            if friendcode == str(NOCHANGEPARAM): FRIENDCODE = userdata[cmddix["friendcode"]]
            else:
                cfc = self.userfunc.check_friendcode(friendcode)
                #[ERROR] 指定のフレンドコード入力規則に合致しない場合
                if cfc != True: 
                    error = "入力されたフレンドコードが指定の入力規則に合致しませんでした。ハイフンを含めて半角数字12桁でフレンドコードを入力してください"
                    raise UserMenuError(error)
                else: FRIENDCODE = friendcode
            #【TwitterID確定】
            if twitterid == str(NOCHANGEPARAM): TWITTERID = userdata[cmddix["twitterid"]]
            else: 
                cti = self.userfunc.check_twitterid(twitterid)
                #[ERROR] 正しいTwitterIDの入力がされなかった場合
                if cti != True: 
                    error = "入力されたTwitterIDが指定の入力規則に合致しませんでした。半角英数字15桁(@なし)でTwitterIDを入力してください"
                    raise UserMenuError(error)
                else: TWITTERID = "@"+twitterid
            #【ポジション確定】
            if position.value == NOCHANGEPARAM: POSITION = userdata[cmddix["position"]]
            else: POSITION = position.name
            #【持ちブキ確定】
            if buki.value == NOCHANGEPARAM: BUKI = userdata[cmddix["buki"]]
            else: BUKI = buki.name
            #【最高XP(エリア)確定】
            if splatzone_xp == NOCHANGEPARAM: SPLATZONE_XP = userdata[cmddix["splatzone_xp"]]
            else: SPLATZONE_XP = splatzone_xp
            #【最高XP(全ルール)確定】
            if allmode_xp == NOCHANGEPARAM: ALLMODE_XP = userdata[cmddix["allmode_xp"]]
            else: ALLMODE_XP = allmode_xp
            #【ウデマエ画像1確定】
            if image1 == None: IMAGE1 = userdata[cmddix["image1"]]
            else:
                ciwh1 = [image1.width, image1.height]
                #[ERROR] 添付ファイルが画像ではなかった場合
                if None in ciwh1:
                    error = "添付されたファイルは画像形式ではありません。ウデマエ画像は画像形式のファイルで、BomuLeagueの提出規格に沿った画像を提出してください"
                    raise UserMenuError(error)
                #[ERROR] 添付画像が1920×1080のゲーム内画像であった場合
                if image1.width == 1920 and image1.height == 1080:
                    error = "添付されたウデマエ画像がゲーム内画像であると判定されました。ウデマエ画像はBomuLeagueの提出規格に沿った画像を提出してください"
                    raise UserMenuError(error)
                else: IMAGE1 = image1.url
            #【ウデマエ画像2確定】
            if image2 == None:
                if apptype == 0: IMAGE2 = ''
                elif apptype == 1: IMAGE2 = userdata[cmddix["image2"]]
            else:
                ciwh2 = [image2.width, image2.height]
                #[ERROR] 添付ファイルが画像ではなかった場合
                if None in ciwh2:
                    error = "添付されたファイルは画像形式ではありません。ウデマエ画像は画像形式のファイルで、BomuLeagueの提出規格に沿った画像を提出してください"
                    raise UserMenuError(error)
                #[ERROR] 添付画像が1920×1080のゲーム内画像であった場合
                if image2.width == 1920 and image2.height == 1080:
                    error = "添付されたウデマエ画像がゲーム内画像であると判定されました。ウデマエ画像はBomuLeagueの提出規格に沿った画像を提出してください"
                    raise UserMenuError(error)
                else: IMAGE2 = image2.url
            #【登録日時確定】
            currenttime = get_currenttime()
            if apptype == 0: REGISTRATION_DATE = currenttime
            elif apptype == 1: REGISTRATION_DATE = str(userdata[cmddix["registration_date"]])

            #【ユーザ情報作成処理】
            postdata = {"名前":NAME, "フレンドコード":FRIENDCODE, "TwitterID":TWITTERID, "Discord名":str(user), "DiscordID":str(user.id),
                        "ポジション":POSITION, "持ちブキ":BUKI, "最高XP(エリア)":SPLATZONE_XP, "最高XP(全ルール)":ALLMODE_XP, "ウデマエ画像1":IMAGE1, "ウデマエ画像2":IMAGE2,
                        "登録日時":REGISTRATION_DATE, "最終更新日時":currenttime}

            #【POST処理】
            await self.userdbfunc.post_userdata(userid=user.id, postdata=postdata, apptype=apptype) #ユーザ情報送信
            await self.userdbfunc.log_userdata(author=author, postdata=postdata, currenttime=currenttime, apptype=apptype) #ログ送信

        except UserMenuError as e:
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(description=str(e)))

        except Exception as e:
            error = "コマンド実行中に予期せぬエラーが発生しました。このエラーが発生した場合は運営まで連絡をお願いします。\nエラー内容:"+str(e)
            print(error)
            await interaction.followup.send(content=author.mention, embed=self.custembed.error(error))

        else:
            #【完了送信処理】
            success = f"{author.mention}から{user.mention}のユーザ情報{apptype_str}を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))


async def setup(client: commands.Bot):
    await client.add_cog(ApplyUser(client))
    