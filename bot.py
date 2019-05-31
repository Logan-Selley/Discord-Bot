import discord
import logging
import sys
from discord.ext import commands
from cogs import music, ErrorHandler, General
import config

cfg = config.load_config()

bot = commands.Bot(command_prefix=cfg["prefix"], case_insensitive=True)
bot.remove_command('help')


COGS = ['cogs.music', 'cogs.ErrorHandler', 'cogs.General']


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
