import discord
import random
from discord.ext import commands
from discord.utils import get

'''
    Commands to add:
        change prefix                       !pre
        youtube/spotify play/search         !p  !play [required argument]
        queue                               !q  !queue
        lyrics of now playing/given song    !ly !lyrics [optional argument]
        display all commands                !help  !commands
        join/disconnect                     !j/!l   !join/!leave
        now playing                         !np !so  !nowplaying !song
        looping playlist/queue/song         !loop   [required argument]
        remove song                         !re !remove [required argument]
        seek to certain point of song       !seek   [required argument]
        pause/resume                        !pa/!r  !pause/!resume
        skip/skipto                         !s  !skip   [optional argument]
        forward/rewind                      !f/!rw  !forward/!rewind    [required argument]
        move song position in queue         !move   [required argument] [required argument]
        clear queue                         !c  !clear
        remove duplicates                   !dupe   !d
        volume                              !v  !volume     [required argument]
        shuffle                             !shuff  !shuffle
        play: add to top of queue           !p/!play [required argument] [required argument]
        play: add to top of queue and skip current  !p/!play [required argument] [required argument]
        
        
'''
'''API keys'''
spotify = None
youtube = None
prefix = '!'
players = {}
'''Queue storage'''
bot = commands.Bot(command_prefix=prefix,  case_insensitive=True)

@bot.event
async def on_ready():
    print('bot ready')


@bot.command(pass_context=True, name='ping')
async def ping(ctx):
    await ctx.send('pong')


@bot.command(pass_context=True, name='join', aliases=['j'])
async def join(ctx):
    author = ctx.message.author
    channel = author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return
    if author.voice.afk:
        await ctx.send("That's the afk channel fam I'm not going in there")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()


@bot.command(pass_context=True, name='leave', aliases=['l'])
async def leave(ctx):
    server = ctx.message.server
    voice_client = bot.voice.channel(server)
    await voice_client.disconnect()


@bot.command(pass_context=True, name='pre', aliases=['prefix'])
async def pre(ctx, fix):
    await ctx.send('Prefix changed to: ' + fix)
    global bot
    bot = commands.Bot(command_prefix=fix)
    return bot


@bot.command(pass_context=True, name='play', aliases=['p'])
async def play(ctx, url):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url)
    players[server.id] = player
    player.start()


@bot.command()
async def queue(ctx):
    print('queue')


@bot.command()
async def lyrics(ctx, arg):
    if arg is None:
        print('given song lyrics')
    else:
        print('current lyrics')


@bot.command()
async def commands(ctx):
    print('commands')


@bot.command()
async def shuffle(self, ctx):
    print('shuffle')

bot.run('NTcwMTIxNzQzODk3ODUzOTgw.XL9N-g.tba2fsgHUHlP6A0kejPLWJeelMw')