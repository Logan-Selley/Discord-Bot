import discord
import random
import youtube_dl
import asyncio
import spotipy
from discord.ext import commands
from discord.utils import get

'''
    Commands to add:
        change prefix                       !pre                                        In Progress
        youtube/spotify play/search         !p  !play [required argument]               In Progress
        queue                               !q  !queue                                  In Progress
        lyrics of now playing/given song    !ly !lyrics [optional argument]
        display all commands                !help  !commands
        join/disconnect                     !j/!l   !join/!leave                        COMPLETE
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

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

'''API keys'''
spotify = None
youtube = None
prefix = '!'
players = {}
'''Queue storage'''
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix),  case_insensitive=True)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='join', aliases=['j'])
    async def join(self, ctx):
        author = ctx.message.author
        try:
            channel = author.voice.channel
        except:
            await ctx.send("You are not connected to a voice channel")
            return
        if author.voice.afk:
            await ctx.send("That's the afk channel fam I'm not going in there")
            return
        voice = ctx.voice_client
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

    @commands.command(pass_context=True, name='leave', aliases=['l'])
    async def leave(self, ctx):
        voice = ctx.voice_client
        await voice.disconnect()

    @commands.command(pass_context=True, name='plays', aliases=['p'])
    async def play(self, ctx, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel")
                raise commands.CommandError("Author not connected to a voice channel")

    @commands.command(pass_context=True, name='play', aliases=['v'])
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel")

        ctx.voice_client.source.volume = volume/100
        await ctx.voice_client.disconnect()


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.command(pass_context=True, name='ping')
async def ping(ctx):
    await ctx.send('pong')


@bot.command(pass_context=True, name='pre', aliases=['prefix'])
async def pre(ctx, fix):
    await ctx.send('Prefix changed to: ' + fix)
    global bot
    bot = commands.Bot(command_prefix=fix)
    return bot


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
async def shuffle(self, ctx):
    print('shuffle')

bot.add_cog(Music(bot))
bot.run('NTcwMTIxNzQzODk3ODUzOTgw.XL9N-g.tba2fsgHUHlP6A0kejPLWJeelMw')