import discord
import random
import youtube_dl
import asyncio
import spotipy
import logging
from discord.ext import commands
from video import Video
import config


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
        skip/skipto                         !s  !skip   [optional argument]             NEEDS TESTING
        forward/rewind                      !f/!rw  !forward/!rewind    [required argument]
        move song position in queue         !move   [required argument] [required argument] NEEDS TESTING
        clear queue                         !c  !clear                                  NEEDS TESTING
        remove duplicates                   !dupe   !d
        volume                              !v  !volume     [required argument]         COMPLETE
        shuffle                             !shuff  !shuffle                            NEEDS TESTING
        play: add to top of queue           !p/!play [required argument] [required argument]
        play: add to top of queue and skip current  !p/!play [required argument] [required argument]
        
        
'''

'''API keys'''
spotify = None


class GuildState:

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None


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


cfg = config.load_config()


def setup(bot):
    bot.add_cog(Music(bot, cfg))


class Music(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config[__name__.split(".")[-1]]
        self.states = {}

    def get_state(self, guild):
        # Gets or creates the state for the given guild
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

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

    @commands.check(in_voice)
    @commands.guild_only()
    @commands.command(pass_context=True, name='play', aliases=['p'])
    async def play(self, ctx, url):
        voice = ctx.voice_client
        state = self.get_state(ctx.guild)

        if voice and voice.channel:
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                logging.warn(f"Error downloading video: {e}")
                await ctx.send(
                    "There was an error donwloading your video"
                )
                return
            state.playlist.append(video)
            message = await ctx.send(
                "Added to queue.", embed=video.get_embed()
            )
            if voice.source:
                self._play_song(voice, state, video)
                message = await ctx.send("", embed=video.get_embed())
                logging.info(f"Now Playing '{video.title}'")
        else:
            raise commands.CommandError(
                "I'm not in a voice channel yet!"
            )

    def _play_song(self, voice, state, song):
        state.now_playing = song
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url), volume=state.volume
        )

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(voice, state, next_song)

        voice.play(source, after=after_playing)

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='volume', aliases=['v'])
    async def volume(self, ctx, volume: int):
        state = self.get_state(ctx.guild)

        if volume < 0:
            volume = 0

        max_vol = self.config["max_volume"]
        if max_vol > -1:
            if volume > max_vol:
                volume = max_vol

        voice = ctx.voice_client
        state.volume = float(volume) / 100.0
        voice.source.volume = state.volume

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

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='skip', aliases=['s'])
    async def skip(self, ctx):
        state = self.get_state(ctx.guild)
        voice = ctx.voice_client
        voice.stop()

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(pass_context=True, name='now playing', aliases=['np'])
    async def now_playing(self, ctx):
        state = self.get_state(ctx.guild)
        message = await ctx.send("", embbed=state.now_playing.get_embed())

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(name='clear', aliases=['c'])
    async def clear(self, ctx):
        state = self.get_state(ctx.guild)
        state.playlist = []

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(name='shuffle', aliases=['sh'])
    async def shuffle(self, ctx):
        state = self.get_state(ctx.guild)
        random.shuffle(state.playlist)
        await ctx.send("Shuffled!")

    @commands.guild_only()
    @commands.check(in_voice)
    @commands.check(audio_playing)
    @commands.command(pass_context=True, name='skipto', aliases=['s2', 'stwo', 'sto'])
    async def skipto(self, ctx, index: int):
        state = self.get_state(ctx.guild)
        if index is None:
            raise commands.CommandError('No index given')
        elif index < 1 or index > len(state.playlist):
            raise commands.CommandError('invalid index')
        else:
            state.playlist = state.playlist[index:]
            await ctx.send(self._queue_text(state.playlist))

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='move', aliases=['m'])
    async def move(self, ctx, song: int, new_index: int):
        state = self.get_state(ctx.guild)
        if 1 <= song <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song - 1)  # take song at index...
            state.playlist.insert(new_index - 1, song)  # and insert it.

            await ctx.send(self._queue_text(state.playlist))
        else:
            raise commands.CommandError("You must use a valid index.")

    @commands.guild_only
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='remove', aliases='r')
    async def remove(self, ctx, index: int):
        state = self.get_state(ctx.guild)
        if index is None or index < 1 or index > len(state.playlist):
            raise commands.CommandError("invalid index")
        else:
            state.playlist.remove(index)
            await ctx.send(self._queue_text(state.playlist))