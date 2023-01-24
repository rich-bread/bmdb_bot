import discord
from discord.ext import commands
from discord import app_commands

usermenu_data = {}

class UserMenu(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="usermenu", description="BomuLeagueの参加者が使えるメニューコマンドです")
    async def usermenu(self, interaction: discord.Interaction):
        await interaction.response.defer(content="Hello")

    @app_commands.command(name=usermenu_data[""],description="")
    async def usermenu_indiv(self,interaction:discord.Interaction):
        await interaction.response.defer(content="")

    #ユーザ情報登録・更新コマンド
    
    

import json

class UserSelectMenu(discord.ui.Select):
    def __init__(self):
        #メニュー一覧が入ってるjsonを開く
        path = ''
        with open(path, encoding='utf-8') as f:
            smf = json.load(f)
        options = [discord.SelectOption(label=m['label'],description=m['label'],emoji=m['emoji'],value=m['value']) for m in smf['options']]
        super().__init__(placeholder=smf['placeholder'], options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

class UserSelectMenuView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(UserSelectMenu())

class UserMenuFunctions():
    def __init__(self):
        pass

class UserMenuData():
    def __init__(self):
        pass #JSON読み込み

    def get_data(self, key):
        pass

    

async def setup(client: commands.Bot):
    await client.add_cog(UserMenu(client))