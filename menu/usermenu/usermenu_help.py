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

#app_commandsで使うデータ
cmddata = open_json(r'menu/usermenu/data/usermenu_help.json')
cmdname = cmddata["name"]
cmddesp = cmddata["description"]

class UserMenu_Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custembed = cmmod.discord_module.CustomEmbed()

    @app_commands.command(name=cmdname, description=cmddesp)
    async def usermenu_help(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        author = interaction.user #コマンド実行者

        cmds = cmddata["commands"]
        helps = []
        for c in cmds:
            cd = open_json(rf'menu/usermenu/data/{c}.json')
            help = f"`/{cd['name']}` {cd['description']}"
            helps.append(help)

        await interaction.followup.send(content=author.mention, embed=self.custembed.default(title=cmddata["title"],description='\n'.join(helps)))

async def setup(client: commands.Bot):
    await client.add_cog(UserMenu_Help(client))
