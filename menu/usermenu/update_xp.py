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
from usermenu.cmfunc.userfunc import UserFunc, UserDBFunc
from usermenu.error.usermenu_error import UserMenuError

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/update_xp.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]
usercmddata = open_json(r'menu/usermenu/data/apply_user.json')
usercmddesb = usercmddata["describe"]
userddix = usercmddata["dataindex"]

class UpdateXP(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = CustomEmbed()
        self.userfunc = UserFunc()
        self.userdbfunc = UserDBFunc()
    
    @app_commands.command(name=cmdname, description=cmddesp)
    @app_commands.describe(user=usercmddesb["user"],splatzone_xp=usercmddesb["splatzone_xp"],allmode_xp=usercmddesb["allmode_xp"],image1=usercmddesb["image1"],image2=usercmddesb["image2"])
    @app_commands.guild_only()
    async def update_xp(self, interaction:discord.Interaction, user:discord.User, splatzone_xp:int, allmode_xp:int, image1:discord.Attachment, image2:discord.Attachment=None) -> None:
        author = interaction.user #コマンド実行者
        try:
            #【thinking処理】
            await interaction.response.defer(thinking=True)
            
            #【ユーザ情報確認処理】
            raw_userdata = await self.userdbfunc.get_userdata(userid=user.id)
            userdata = raw_userdata[0]
            #[ERROR] ユーザ情報がDBに存在しない場合
            if not userdata:
                error = "このコマンドは情報登録済みのユーザのみが使用できます。ユーザ情報登録を行ってから、このコマンドを実行してください"
                raise UserMenuError(error)
            
            #【ウデマエ画像1確定】
            ciwh1 = [image1.width, image1.height]
            #[ERROR] 添付ファイルが画像ではなかった場合
            if None in ciwh1:
                error = "添付されたファイルは画像形式ではありません。ウデマエ画像は画像形式のファイルで、BomuLeagueの提出規格に沿った画像を提出してください"
                raise UserMenuError(error)
            #[ERROR] 添付画像が1920×1080のゲーム内画像であった場合
            if image1.width == 1920 and image1.height == 1080:
                error = "添付されたウデマエ画像がゲーム内画像であると判定されました。ウデマエ画像はBomuLeagueの提出規格に沿った画像を提出してください"
                raise UserMenuError(error)
            
            #【ウデマエ画像2確定】
            if image2 == None: image2 = userdata[userddix["image2"]]
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
                
            #【必要項目確定】
            apptype = 1 #申請区分 ※情報登録済ユーザしか使用できない為
            currenttime = get_currenttime()
            #【ユーザ情報作成処理】
            postdata = {"名前":userdata[userddix["name"]], "フレンドコード":userdata[userddix["friendcode"]],"TwitterID":userdata[userddix["twitterid"]],
                        "Discord名":str(user), "DiscordID":str(user.id), "ポジション":userdata[userddix["position"]], "持ちブキ":userdata[userddix["buki"]],
                        "最高XP(エリア)":splatzone_xp, "最高XP(全ルール)":allmode_xp, "ウデマエ画像1":str(image1), "ウデマエ画像2":str(image2),
                        "登録日時":userdata[userddix["registration_date"]], "最終更新日時":currenttime}
            
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
            #【完了通知処理】
            success = f"{author.mention}から{user.mention}のユーザ情報更新【XP更新】を受け付けました。データベースからの完了通知をお待ちください。通知が無かった場合は運営まで連絡をお願いします"
            await interaction.followup.send(content=author.mention, embed=self.custembed.success(success))

async def setup(client: commands.Bot):
    await client.add_cog(UpdateXP(client))
    