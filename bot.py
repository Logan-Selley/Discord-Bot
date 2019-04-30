import discord
import spotipy
import random
import asyncio
from discord.ext import commands

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
'''Queue storage'''
queue = asyncio.Queue()
play_next = asyncio.Event()
bot = commands.Bot(command_prefix=prefix,  case_insensitive=True)

@bot.event
async def on_ready():
    print('bot ready')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')


''' Not working '''
@bot.command(pass_context = True)
async def pre(ctx, fix):
    await ctx.send('Prefix changed to: ' + fix)
    global bot
    bot = commands.Bot(command_prefix=fix)
    return bot


@bot.command(pass_context = True, name = 'play', aliases=['p', 'Test', 'P'])
async def play(ctx, term, var):
    url = None
    if term=="top":
        url = var

    elif term=="topskip":
        url = var

    else:
        url = term

    if not bot.is_voice_connected(ctx.message.server):
        voice = await bot.join_voice_channel(ctx.message.author.voice_channel)
    else:
        voice = bot.voice_client_in(ctx.message.server)

    player = await voice.create_ytdl_player(url, after=toggle_next)
    await queue.put(player)

async def audio_player_task():
    while True:
        play_next.clear()
        current = await queue.get()
        current.start()
        await play_next.wait()


def toggle_next():
    bot.loop.call_soon_threadsafe(play_next.set)


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
async def help(self, ctx):
    print('help')


@bot.command()
async def shuffle(self, ctx):
    print('shuffle')

bot.loop.create_task(audio_player_task())

bot.run('NTcwMTIxNzQzODk3ODUzOTgw.XL9N-g.tba2fsgHUHlP6A0kejPLWJeelMw')