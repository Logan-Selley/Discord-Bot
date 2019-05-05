import discord
import logging
import sys
from discord.ext import commands
from cogs import music
import config

cfg = config.load_config()

bot = commands.Bot(command_prefix=cfg["prefix"], case_insensitive=True)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.command(pass_context=True, name='ping')
async def ping(ctx):
    await ctx.send('pong')


@bot.command(pass_context=True, name='pre', aliases=['prefix'])
async def pre(ctx, fix):
    await ctx.send('Prefix changed to: ' + fix)
    global bot
    bot = commands.Bot(command_prefix=fix)
    return bot

COGS = [music.Music]


def add_cogs(bot):
    for cog in COGS:
        bot.load_extension(music.Music)


def run():
    add_cogs(bot)
    if cfg["token"] == "":
        raise ValueError(
            "No Token provided"
        )
    bot.run(cfg["token"])
