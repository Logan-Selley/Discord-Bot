import discord
import logging
import sys
import discord
from discord.ext import commands
from cogs import music, ErrorHandler, General, Moderation, APIs
import config
import asyncio

cfg = config.load_config()

bot = commands.Bot(command_prefix=cfg["prefix"], case_insensitive=True)
bot.remove_command('help')


COGS = ['cogs.music', 'cogs.ErrorHandler', 'cogs.General', 'cogs.Moderation', 'cogs.APIs']


def add_cogs(bot):
    print("cogs:")
    for cog in COGS:
        print(cog)
        bot.load_extension(cog)


def run():
    add_cogs(bot)
    if cfg["token"] == "":
        raise ValueError(
            "No Token provided"
        )
    bot.run(cfg["token"])


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')
    await bot.change_presence(activity=discord.Game(cfg["prefix"] + "help for commands"))
