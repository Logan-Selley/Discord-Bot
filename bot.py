import discord
import random
import youtube_dl
import asyncio
import spotipy
from discord.ext import commands

'''
    Commands to add:
        change prefix                       !pre                                        BROKEN
        youtube/spotify play/search         !p  !play [required argument]               IN PROGRESS
        queue                               !q  !queue                                  NEEDS TESTING
        lyrics of now playing/given song    !ly !lyrics [optional argument]
        display all commands                !help
        join/disconnect                     !j/!l   !join/!leave                        COMPLETE
        now playing                         !np !so  !nowplaying !song                  COMPLETE
        looping playlist/queue/song         !loop   [required argument]
        remove song                         !re !remove [required argument]
        seek to certain point of song       !seek   [required argument]
        pause/resume                        !pa/!r  !pause/!resume                      COMPLETE
        skip/skipto                         !s  !skip   [optional argument]             IN PROGRESS
        forward/rewind                      !f/!rw  !forward/!rewind    [required argument]
        move song position in queue         !move   [required argument] [required argument]
        clear queue                         !c  !clear                                  NEEDS TESTING
        remove duplicates                   !dupe   !d
        volume                              !v  !volume     [required argument]         COMPLETE
        shuffle                             !shuff  !shuffle                            IN PROGRESS
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
prefix = '!'


bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix),  case_insensitive=True)


class GuildState:

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None


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


async def audio_playing(ctx):
    client = ctx.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise commands.CommandError("Not currently playing audio")


async def in_voice(ctx):
    voice = ctx.author.voice
    bot_voice = ctx.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise commands.CommandError("You need to be in the channel to do that")


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.audio_player_task())
        self.states = {}

    def get_state(self, guild):
        # Gets or creates the state for the given guild
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    async def audio_player_task(self):
        while True:
            self.play_next.clear()
            self.player = await self.songs.get()
            self.voice.play(self.player, after=lambda e: print('Player error: %s' % e) if e else None)
            self.userQueue.remove(self.player.title)
            await self.server.send('Now playing: {}'.format(self.player.title))
            await self.play_next.wait()

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
            await channel.connect()

    @commands.guild_only()
    @commands.command(pass_context=True, name='leave', aliases=['l'])
    async def leave(self, ctx):
        voice = ctx.voice_client
        state = self.get_state(ctx.guild)
        if voice and voice.channel:
            await voice.disconnect()
            state.playlist = []
            state.now_playing = None
        else:
            raise commands.CommandError("Not in a voice channel")

    @commands.command(pass_context=True, name='play', aliases=['p'])
    async def play(self, ctx, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            await ctx.send('Enqueued: {}'.format(player.title))
            self.userQueue.append(player.title)
            await self.songs.put(player)
        self.voice = ctx.voice_client
        self.server = ctx
        await ctx.message.delete()

    @commands.command(pass_context=True, name='volume', aliases=['v'])
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel")
        if volume < 0:
            volume = 0
        ctx.voice_client.source.volume = volume/100

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='pause', aliases=['pa'])
    async def pause(self, ctx):
        if ctx.voice_client.is_playing:
            ctx.voice_client.pause()

    @commands.command(pass_context=True, name='resume', aliases=['r'])
    async def resume(self, ctx):
        ctx.voice_client.resume()

    @commands.command(pass_context=True, name='stop', aliases=['st'])
    async def stop(self, ctx):
        ctx.voice_client.stop()

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(pass_context=True, name='queue', aliases=['q'])
    async def queue(self, ctx):
        state = self.get_state(ctx.guild)
        await ctx.send(self._queue_text(state.playlist))

    def _queue_text(self, queue):
        if len(queue) > 0:
            message = [f"{len(queue)} songs in queue:"]
            message += [
                f"  {index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]
            return "\n".join(message)
        else:
            return "The queue is empty"

    @commands.command(pass_context=True, name='skip', aliases=['s'])
    async def skip(self, ctx):
        try:
            self.voice.stop()
            self.play_next.set()
        except:
            ctx.send("nothing to skip")

    @commands.command(pass_context=True, name='now playing', aliases=['np'])
    async def now_playing(self, ctx):
        try:
            await ctx.send('Now playing: {}'.format(self.player.title))
        except AttributeError:
            await ctx.send('Not currently playing')

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(name='clear', aliases=['c'])
    async def clear(self, ctx):
        state = self.get_state(ctx.guild)
        state.playlist = []

    @commands.command(name='shuffle', aliases=['sh'])
    async def shuffle(self, ctx):
        await ctx.send('Shuffling...')

    @commands.command(pass_context=True, name='skipto', aliases=['s2', 'stwo', 'sto'])
    async def skipto(self, ctx, index: int):
        if index is None:
            await ctx.send('No index given')


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


bot.add_cog(Music(bot))
bot.run('')
