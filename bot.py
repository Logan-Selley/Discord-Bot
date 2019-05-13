import discord
import logging
import sys
from discord.ext import commands
from cogs import music
import config

cfg = config.load_config()

bot = commands.Bot(command_prefix=cfg["prefix"], case_insensitive=True)
bot.remove_command('help')


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.command(pass_context=True, name='ping')
async def ping(ctx):
    await ctx.send('pong')


@bot.command(name='help')
async def help(ctx):
    prefix = cfg["prefix"]
    commands = {}

    # MUSIC
    commands[prefix + "join"] = "bot joins the user's voice channel"
    commands[prefix + "leave"] = "bot leaves it's current voice channel"
    commands[prefix + "play"] = "adds the given URL or search query to the music queue"
    commands[prefix + "pause"] = "pause the bot's music playback"
    commands[prefix + "resume"] = "resume the bot's music playback"
    commands[prefix + "skip"] = "skip the current song playing"
    commands[prefix + "skipto"] = "skip to a specific song in the queue by it's queue number"
    commands[prefix + "queue"] = "display the current queue"
    commands[prefix + "clear"] = "clear the current queue"
    commands[prefix + "volume"] = "change the volume of music playback by setting a new volume value"
    commands[prefix + "shuffle"] = "shuffles the current queue"
    commands[prefix + "nowplaying"] = "display the current song plaaying"
    commands[prefix + "lyrics"] = "search and show the lyrics of the current song or the given search query"

    # GENERAL
    commands[prefix + "help"] = "You just called this command, congrats"
    commands[prefix + "ping"] = "test the bot's responsiveness"
    commands[prefix + "prefix"] = "display the current command prefix"

    msg = discord.Embed(title="temp", description="Bot written by Logan Selley in Python 3"
                                                  " using the discord.py library")
    for command, description in commands.items():
        msg.add_field(name=command, value=description, inline=False)

    await ctx.send(msg)


@bot.command(pass_context=True, name='pre', aliases=['prefix'])
async def pre(ctx):
    await ctx.send('Current prefix: ' + cfg["prefix"])

COGS = ['cogs.music']


def add_cogs(bot):
    print("cogs")
    for cog in COGS:
        bot.load_extension(cog)


def run():
    add_cogs(bot)
    if cfg["token"] == "":
        raise ValueError(
            "No Token provided"
        )
    bot.run(cfg["token"])
