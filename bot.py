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

    if message.author.bot:
        return
    if message.channel.is_private:
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

