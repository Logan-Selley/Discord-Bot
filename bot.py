import discord
import logging
import sys
import discord
from discord.ext import commands
from cogs import music, ErrorHandler, General, Moderation, APIs
import config
import asyncio
import time
import random
import json

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


@bot.event
async def on_member_join(member):
    msg = cfg["welcome"]
    await member.send(msg)


@bot.event
async def on_member_remove(member):
    msg = cfg["goodbye"]
    await member.send(msg)


@bot.event
async def on_message(message):
    xp = config.load_xp()
    if message.author.bot:
        return
    if message.guild is None:
        return
    else:
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
