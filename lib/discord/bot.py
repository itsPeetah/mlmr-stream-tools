import os
import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        super().__init__("&", intents=discord.Intents.all())
        self.token = os.getenv("DISCORD_BOT_TOKEN")
    def run(self):
        super().run(self.token)