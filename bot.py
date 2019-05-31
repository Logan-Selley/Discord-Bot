import discord
import logging
import sys
from discord.ext import commands
from cogs import music, ErrorHandler
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


@bot.command(pass_context=True, name='wink')
async def wink(ctx):
    await ctx.send('wonk')


@bot.command(name='help')
async def help(ctx, *args):
    if len(args) > 1:
        await ctx.send("That's not a command or command group!")
        return
    prefix = cfg["prefix"]
    arg = args[0]
    commands = {}

    # MUSIC
    join = {prefix + "join": "aliases= {j}, bot joins the user's voice channel"}
    leave = {prefix + "leave": "aliases= {l}, bot leaves it's current voice channel"}
    play = {prefix + "play": "aliases= {p}, adds the given Spotify/Youtube url or search query to the music queue"}
    pause = {prefix + "pause": "aliases= {pa}, pauses the bot's music playback"}
    resume = {prefix + "resume": "aliases= {re}, resumes the bot's music playback"}
    skip = {prefix + "skip": "aliases= {s}, skips the current track"}
    skipto = {prefix + "skipto": "aliases= {s2, skip2, sto}, skip to a specific track in the queue by it's queue "
                                 "number"}
    queue = {prefix + "queue": "aliases= {q}, displays the current song queue"}
    clear = {prefix + "clear": "aliases= {c}, clears the current queue of all tracks"}
    volume = {prefix + "volume": "aliases= {v}, either displays the current volume or changes it to the given number"}
    shuffle = {prefix + "shuffle": "aliases= {shuff, sh}, shuffles the current queue"}
    nowplaying = {prefix + "nowplaying": "aliases= {np}, displays the currently playing track"}
    lyrics = {prefix + "lyrics": "aliases= {ly}, displays the current track's lyrics or lyrics of the given song title"}
    duplicates = {prefix + "duplicates": "aliases= {dupe, d}, removes duplicate tracks from the music queue"}
    removeusersongs = {prefix + "removeusersongs": "aliases= {rus}, removes all songs requested by the given user"
                                                   "works with nicknames/displaynames"}
    seek = {prefix + "seek": "aliases= {}, start the current track at the given timestamp, form: 2:20 for"
                             "2 minutes, 20 seconds"}
    playlist = {prefix + "playlist": "aliases= {pl}, adds the first 100 tracks from the given spotify/youtube url to"
                                     "the queue"}


    # GENERAL
    help = {}
    commands[prefix + "help"] = "You just called this command, congrats"
    commands[prefix + "ping"] = "test the bot's responsiveness"
    commands[prefix + "prefix: pre"] = "display the current command prefix"
    commands[prefix + "loop: looping"] = "loop song/playlist by giving arg 'song' or 'queue', turn off with 'off'"

    msg = discord.Embed(title="Very Sad Intern", description="Bot written by Logan Selley in Python 3"
                                                             " using the discord.py library")
    for command, description in commands.items():
        msg.add_field(name=command, value=description, inline=False)

    await ctx.send("", embed=msg)


@bot.command(pass_context=True, name='pre', aliases=['prefix'])
async def pre(ctx):
    await ctx.send('Current prefix: ' + cfg["prefix"])

COGS = ['cogs.music', 'cogs.ErrorHandler']


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
