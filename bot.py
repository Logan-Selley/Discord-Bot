import discord
from discord.exe import commands

prefix = '!'
bot = commands.bot(command_prefix=prefix)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run('NTcwMTIxNzQzODk3ODUzOTgw.XL9N-g.tba2fsgHUHlP6A0kejPLWJeelMw')
