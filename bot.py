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
    xp = config.load_xp
    print(xp)
    if message.author.bot:
        return
    if message.guild is None:
        return
    else:
        guild = message.guild
        guilds = xp["guilds"]
        if guild.id not in guilds:
            guilds[guild.id] = {}
        guild_xp = guilds[guild.id]
        user = message.author.id
        if user not in guild_xp:
            guild_xp[user] = {}
            guild_xp[user]["xp"] = 0
            guild_xp[user]["level"] = 0
            guild_xp[user]["last_message"] = 0
        xp = random.randint(5, 10)
        await add_xp(guild_xp[user], xp)
        await level_up(guild_xp[user], message.channel, message.author.display_name)

        with open("./experience.json", "w") as f:
            json.dump(xp, f)
        print("xp updated")


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

    print(lvl_end)
    print(lvl_start)
