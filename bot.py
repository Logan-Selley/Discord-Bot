import discord
from discord.ext import commands

'''
    Commands to add:
        change prefix                       !pre
        youtube/spotify play/search         !p  !play [required argument]
        queue                               !q  !queue
        lyrics of now playing/given song    !ly !lyrics [optional argument]
        display all commands                !?  !commands
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

prefix = '!'
bot = commands.Bot(command_prefix=prefix)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


''' Not working '''
@bot.command()
async def pre(ctx, fix):
    await ctx.send('Prefix changed to: ' + fix)
    global bot
    bot = commands.Bot(command_prefix=fix)
    return bot



bot.run('NTcwMTIxNzQzODk3ODUzOTgw.XL9N-g.tba2fsgHUHlP6A0kejPLWJeelMw')
