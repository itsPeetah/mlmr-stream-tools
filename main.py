import os
from dotenv import load_dotenv
from discord.ext import commands as d_commands
from lib.discord import Bot as DiscordBot

load_dotenv()

d_bot = DiscordBot()

@d_bot.command()
async def hello(ctx:d_commands.Context):
    await ctx.send("Hello, world!")

@d_bot.event
async def on_ready():
    print(f'{d_bot.user} has connected to Discord!')
    for guild in d_bot.guilds:
        print(guild.id, guild.name)

d_bot.run()