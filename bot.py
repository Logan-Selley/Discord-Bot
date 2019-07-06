import discord
import logging
import sys
import discord
from discord.ext import commands
from discord.utils import find
from cogs import music, ErrorHandler, General, Moderation, APIs
import config
import asyncio
import time
import random
import json

cfg = config.load_config()
setting = config.load_settings()


def prefix(bot, message):
    try:
        settings = config.load_settings()
        id = message.guild.id
        return settings['guilds'][str(id)]['prefix']
    except:
        return "!"


bot = commands.Bot(command_prefix=prefix, case_insensitive=True)
bot.remove_command('help')


COGS = ['cogs.music', 'cogs.ErrorHandler', 'cogs.General', 'cogs.Moderation', 'cogs.APIs', 'cogs.Admin']


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
    await bot.change_presence(activity=discord.Game("!help for commands"))


@bot.event
async def on_member_join(member):
    id = member.guild.id
    msg = setting['guilds'][str(id)]['welcome']
    await member.send(msg)


@bot.event
async def on_member_remove(member):
    id = member.guild.id
    msg = setting['guilds'][str(id)]['goodbye']
    await member.send(msg)


@bot.event
async def on_message(message):
    if not message.author.bot and message.guild is not None:
        settings = config.load_settings()
        if settings['guilds'][str(message.guild.id)]["leveling"] is True:
            xp = config.load_xp()
            guild = message.guild
            if str(guild.id) not in xp['guilds']:
                xp['guilds'][str(guild.id)] = {}
            user = message.author.id
            if str(user) not in xp['guilds'][str(guild.id)]:
                xp['guilds'][str(guild.id)][str(user)] = {
                    'xp': 0,
                    'level': 0,
                    'last_message': 0
                }
            exp = random.randint(5, 10)
            await add_xp(xp['guilds'][str(guild.id)][str(user)], exp)
            await level_up(xp['guilds'][str(guild.id)][str(user)], message.channel, message.author.display_name)

            with open("./experience.json", "w") as f:
                json.dump(xp, f)
    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    """Adds guild to settings file with default settings"""
    settings = config.load_settings()
    if str(guild.id) not in settings['guilds']:
        settings['guilds'][str(guild.id)] = {
            "prefix": "!",
            "leveling": True,
            "welcome": "Welcome to the server!",
            "goodbye": "You will be missed!",
            "warn_kick": 3,
            "warn_ban": 5,
            "max_volume": 250
        }
    with open("./settings.json", "w") as f:
        json.dump(settings, f)
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}!'.format(guild.name))


async def add_xp(user, xp):
    if time.time() - user["last_message"] > 30:
        user["xp"] += xp
        user["last_message"] = time.time()
    else:
        return


async def level_up(user, channel, display):
    xp = user["xp"]
    lvl_start = user["level"]
    lvl_end = int(xp ** (1/4))

    if lvl_start < lvl_end:
        await channel.send(display + " leveled up to lvl " + str(lvl_end) + "!")
        user["level"] = lvl_end
