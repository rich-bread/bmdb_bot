import os
import discord
from discord.ext import commands
from colorama import Back, Fore, Style
from datetime import datetime
import platform

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, intents=discord.Intents().all())
        self.cogslist = ['menu.usermenu.apply_user','menu.usermenu.apply_team','menu.usermenu.entry_season',
        'menu.usermenu.check_user','menu.usermenu.check_team','menu.usermenu.get_averagexp','menu.usermenu.withdraw_season', 'menu.usermenu.usermenu_help']

    async def setup_hook(self):
        if self.cogslist:
            for ext in self.cogslist:
                await self.load_extension(ext)

    async def on_ready(self):
        prfx = (Fore.RESET + Style.RESET_ALL + Back.BLACK + Fore.GREEN + datetime.now().strftime(r'%Y-%m-%d %H:%M:%S') + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.YELLOW + self.user.name)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()))
        synced = await self.tree.sync()
        print(prfx + " Slash Commands Synced " + Fore.YELLOW + str(len(synced)) + " Commands")

client = Client()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client.run(TOKEN)