import discord
import random
import youtube_dl as ytdl
import asyncio
import spotipy_edit
import logging
from discord.ext import commands
from video import Video
import config
import utils
from lyrics_extractor import Song_Lyrics
from urlvalidator import validate_url, ValidationError
from spotipy.oauth2 import SpotifyClientCredentials


'''
    Commands to add:
        change prefix                        MOVED TO CONFIG
        prefix  (display)                   !pre                                        COMPLETE
        youtube/search                      !p  !play [required argument]               COMPLETE
        queue                               !q  !queue                                  COMPLETE
        lyrics of now playing/given song    !ly !lyrics [optional argument]             COMPLETE
        display all commands                !help                                       COMPLETE
        join/disconnect                     !j/!l   !join/!leave                        COMPLETE
        now playing                         !np !so  !nowplaying !song                  COMPLETE
        looping playlist/queue/song         !loop   [required argument]                 COMPLETE
        remove song                         !re !remove [required argument]             COMPLETE
        pause/resume                        !pa/!r  !pause/!resume                      COMPLETE
        skip/skipto                         !s  !skip   [optional argument]             COMPLETE
        seek                                !seek [required argument]                   COMPLETE
        move song position in queue         !move   [required argument] [required argument] COMPLETE
        clear queue                         !c  !clear                                  COMPLETE
        remove duplicates                   !dupe   !d                                  COMPLETE
        volume                              !v  !volume     [required argument]         COMPLETE
        shuffle                             !shuff  !shuffle                            COMPLETE
        removeusersongs                     !rus remove songs requested by given user (works with nicknames)  COMPLETE
        playlist                            !pl add playlist (yt or spotify) to queue   COMPLETE
        
        implement vote skip
        
        
        testing notes
        
        
'''


class GuildState:

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None
        self.looping = None


async def audio_playing(ctx):
    client = ctx.voice_client
    if client.is_playing():
        return True
    else:
        await ctx.send("Not currently playing audio")
        raise commands.CommandError("Not currently playing audio")


async def in_voice(ctx):
    voice = ctx.author.voice
    bot_voice = ctx.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        await ctx.send("You need to be in the channel to do that")
        raise commands.CommandError("You aren't in the same channel as me")


cfg = config.load_config()


def setup(bot):
    bot.add_cog(Music(bot, cfg))


class Music(commands.Cog):
    """Play music/playlists from Youtube or Spotify"""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config[__name__.split(".")[-1]]
        self.states = {}
        credentials = SpotifyClientCredentials(client_id=self.config["spotify_client"],
                                               client_secret=self.config["spotify_secret"])
        self.spot = spotipy_edit.Spotify(client_credentials_manager=credentials)

    def get_state(self, guild):
        # Gets or creates the state for the given guild
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.command(pass_context=True, name='join', aliases=['j'])
    async def join(self, ctx):
        """Have the bot join the user's current channel
        Aliases= {j}"""
        author = ctx.message.author
        try:
            channel = author.voice.channel
        except:
            await ctx.send("You are not connected to a voice channel")
            logging.info("author not in voice")
            return
        if author.voice.afk:
            await ctx.send("That's the afk channel fam I'm not going in there")
            logging.info("afk channel attempt")
            return
        voice = ctx.voice_client
        if voice and voice.is_connected():
            await voice.move_to(channel)
            logging.info("moved channels")
        else:
            await channel.connect()
            logging.info("joined voice channel")

    @commands.guild_only()
    @commands.command(pass_context=True, name='leave', aliases=['l'])
    async def leave(self, ctx):
        """Have the bot leave it's current channel
        Aliases= {l}"""
        voice = ctx.voice_client
        state = self.get_state(ctx.guild)
        if voice is not None and voice.is_connected():
            await voice.disconnect()
            if voice.is_connected():
                logging.warning("FAILED TO LEAVE")
                await ctx.send("something went wrong...")
            else:
                state.playlist = []
                state.now_playing = None
                logging.info("left voice")
        else:
            await ctx.send("I'm not in a voice channel")
            raise commands.CommandError("Not in a voice channel")

    @commands.check(in_voice)
    @commands.guild_only()
    @commands.command(pass_context=True, name='play', aliases=['p'])
    async def play(self, ctx, *args):
        """Attempts to play the given input, accepts Youtube video links, or Spotify track links, anything else is treated as a search query
        Aliases= {p}"""
        if len(args) == 0:
            await ctx.send("you're missing parameters!")
            raise commands.CommandError("Missing arguments")
        url = utils.argument_concat(args)
        await self._play(ctx, url, False)

    async def _play(self, ctx, url, playlist):
        voice = ctx.voice_client
        state = self.get_state(ctx.guild)
        if utils.url_validation(url):
            search_type = "url"
        else:
            search_type = "search"
        if voice.is_connected():
            result = None
            logging.info("play type: " + search_type)
            if search_type == "url":
                if "youtube" in url:
                    logging.info("yt url")
                    result = url
                elif "spotify" in url:
                    try:
                        logging.info("spotify url")
                        track = self.spot.track(url)
                        result = track['artists'][0]['name'] + " " + track['name']
                        print(result)
                    except:
                        await ctx.send("invalid spotify url")
            elif search_type == "search":
                try:
                    search = self.spot.search(q=url, limit=1, type='track')
                    track = search['tracks']['items'][0]
                    result = track['artists'][0]['name'] + " " + track['name']
                except:
                    logging.info("search fail")
                    result = url
            try:
                video = Video(result, ctx.author)
            except ytdl.DownloadError as e:
                logging.warning(f"Error downloading video: {e}")
                await ctx.send(
                    "There was an error downloading your video, maybe an invalid url or no search results"
                )
                return
            state.playlist.append(video)
            logging.info(result + " added to queue")
            if not playlist:
                await ctx.send(
                    "Added to queue:", embed=video.get_embed()
                )
                await ctx.message.delete()
            if not voice.is_playing():
                logging.info("cold start")
                self._play_song(voice, state, video, None)
                state.playlist.pop(0)
                await ctx.send("Now Playing:", embed=video.get_embed())

    def _play_song(self, voice, state, song, source):
        state.now_playing = song
        if source is None:
            if song.seek is not None:
                source = song.seek
            else:
                source = self._get_source(song, state)
        logging.info(f"Now Playing '{song.title}'")

        def after_playing(*args):
            if state.looping == "song":
                state.playlist.insert(0, song)
            elif state.looping == "queue":
                state.playlist.append(song)

            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(voice, state, next_song, None)
            else:
                state.now_playing = None
        voice.play(source, after=after_playing)

    @staticmethod
    def _get_source(song, state):
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(source=song.stream_url, before_options='-reconnect 1 -reconnect_streamed 1 '
                                                                          '-reconnect_delay_max 4'),
            volume=state.volume
        )
        return source

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='volume', aliases=['v'])
    async def volume(self, ctx, *args: float):
        """Displays the current playback volume or adjusts it to the given number
        Aliases= {v}"""
        state = self.get_state(ctx.guild)
        if len(args) == 0:
            await ctx.send(str(state.volume * 100))
        else:
            volume = args[0]
            if volume < 0:
                volume = 0

            max_vol = self.config["max_volume"]
            if max_vol > -1:
                if volume > max_vol:
                    volume = max_vol

            voice = ctx.voice_client
            state.volume = float(volume) / 100.0
            voice.source.volume = state.volume
            await ctx.send("volume changed to: " + str(state.volume * 100))

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='pause', aliases=['pa'])
    async def pause(self, ctx):
        """Pauses current audio
        Aliases= {pa}"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(pass_context=True, name='resume', aliases=['re'])
    async def resume(self, ctx):
        """Resumes current audio
        Aliases= {re}"""
        ctx.voice_client.resume()

    @commands.guild_only()
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='queue', aliases=['q'])
    async def queue(self, ctx):
        """Displays the queue of tracks to be played
        Aliases= {q}"""
        state = self.get_state(ctx.guild)
        await self._send_queue(ctx, state.playlist)

    async def _send_queue(self, ctx, queue):
        messages = self._queue_text(queue)
        for string in messages:
            await ctx.send('', embed=string)

    @staticmethod
    def _queue_text(queue):
        messages = []
        if len(queue) > 0:
            message = discord.Embed(title='Current Queue', description=str(len(queue)) + " songs in queue:")
            field_limit = 25
            current_field = 1
            for (index, song) in enumerate(queue):
                if current_field <= field_limit:
                    message.add_field(name=str(index+1) + ": ",
                                      value=song.title + " (requested by " + song.requested_by.display_name + ")",
                                      inline=False)
                    current_field += 1
                else:
                    messages.append(message)
                    message = discord.Embed(title='Current Queue continued',
                                            description=str(len(queue)) + " songs in queue:")
                    message.add_field(name=str(index + 1) + ": ",
                                      value=song.title + " (requested by " + song.requested_by.display_name + ")",
                                      inline=False)
                    current_field = 2
            messages.append(message)
            return messages
        else:
            messages.append(discord.Embed(title='Current Queue', description=str(len(queue)) + " songs in queue:"))
            return messages

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='skip', aliases=['s'])
    async def skip(self, ctx):
        """Skips the current track
        Aliases= {s}"""
        voice = ctx.voice_client
        voice.stop()
        logging.info("skipped audio")
        await ctx.send("skipped!")

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(pass_context=True, name='now playing', aliases=['np'])
    async def now_playing(self, ctx):
        """Displays the current track
        Aliases= {np}"""
        state = self.get_state(ctx.guild)
        await ctx.send("Now Playing: ", embed=state.now_playing.get_embed())

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(name='clear', aliases=['c'])
    async def clear(self, ctx):
        """Removes everything from the queue
        Aliases= {c}"""
        state = self.get_state(ctx.guild)
        state.playlist = []

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.command(name='shuffle', aliases=['sh', 'shuff'])
    async def shuffle(self, ctx):
        """Shuffles the queue order
        Aliases= {shuff, sh}"""
        state = self.get_state(ctx.guild)
        random.shuffle(state.playlist)
        await ctx.send("Shuffled!")
        await ctx.send(self._queue_text(state.playlist))

    @commands.guild_only()
    @commands.check(in_voice)
    @commands.check(audio_playing)
    @commands.command(pass_context=True, name='skipto', aliases=['s2', 'stwo', 'sto', 'skip2'])
    async def skipto(self, ctx, index: int):
        """Skips to the given queue number
        Aliases= {s2, stwo, sto, skip2}"""
        state = self.get_state(ctx.guild)
        if index is None:
            await ctx.send("No index given")
            raise commands.CommandError('No index given')
        elif index < 1 or index > len(state.playlist):
            await ctx.send("invalid index")
            raise commands.CommandError('invalid index')
        else:
            state.playlist = state.playlist[index-1:]
            ctx.voice_client.stop()
            await self._send_queue(ctx, state.playlist)

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='move', aliases=['m'])
    async def move(self, ctx, song: int, new_index: int):
        """Puts the given track (by it's queue number) at the given queue index
        Aliases= {m}"""
        state = self.get_state(ctx.guild)
        if 1 <= song <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song - 1)  # take song at index...
            state.playlist.insert(new_index - 1, song)  # and insert it.

            await self._send_queue(ctx, state.playlist)
        else:
            raise commands.CommandError("You must use a valid index.")

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='remove', aliases=['r'])
    async def remove(self, ctx, index: int):
        """removes the track at the given queue number
        Aliases= {r}"""
        state = self.get_state(ctx.guild)
        index -= 1
        if index is None or index < 1 or index > len(state.playlist):
            raise commands.CommandError("invalid index")
        else:
            del state.playlist[index]
            await self._send_queue(ctx, state.playlist)

    @commands.guild_only()
    @commands.command(pass_context=True, name='lyrics', aliases=['ly'])
    async def lyrics(self, ctx, *args):
        """Displays the lyrics of the current track, or the search query provided
        Aliases= {ly}"""
        state = self.get_state(ctx.guild)
        extract = Song_Lyrics(self.config["search_key"], self.config["search_id"])
        messages = []
        title = None
        lyrics = None
        if len(args) == 0:  # now playing lyrics
            if ctx.voice_client is not None and ctx.voice_client.is_playing():
                playing = state.now_playing
                title, lyrics = extract.get_lyrics(playing.title)
                print(len(lyrics))
                print(lyrics)

            else:
                await ctx.send("Nothing is playing currently, add a song title to the command to search")
                return
        else:  # search lyrics
            song = utils.argument_concat(args)
            if utils.url_validation(song):
                await ctx.send("This doesn't take urls fam, just enter the title of the song")
                return
            title, lyrics = extract.get_lyrics(song)
        message = title + "\n" + lyrics
        if len(message) > 2000:
            while len(message) > 2000:
                index = 2000
                while message[index] != "\n":
                    index -= 1
                mes = message[:index]
                sage = message[index:]
                messages.append(mes)
                message = sage
        else:
            messages.append(message)
        for string in messages:
            await ctx.send(string)

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='duplicates', aliases=['d', 'dupe'])
    async def duplicate(self, ctx):
        """Removes duplicate tracks from the queue
        Aliases= {d, dupe}"""
        state = self.get_state(ctx.guild)
        diction = {}
        for song in state.playlist:
            diction[song.title] = song
        playlist = list(diction.values())
        state.playlist = playlist
        await ctx.send("Duplicates removed!")
        await self._send_queue(ctx, state.playlist)

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='removeusersongs', aliases=['rus'])
    async def remove_user_songs(self, ctx, *args):
        """Removes all tracks requested by the given user, accepts nicknames
        Aliases= {rus}"""
        state = self.get_state(ctx.guild)
        if len(args) == 0:
            await ctx.send("no user given, add a username to delete their songs.")
        else:
            for song in state.playlist:
                if song.requested_by.display_name == args[0]:
                    state.playlist.remove(song)
            await ctx.send("removed all songs requested by: " + args[0])
            await self._send_queue(ctx, state.playlist)

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='seek')
    async def seek(self, ctx, timestamp):
        """Moves the current tracks audio playback to the given timestamp, eg: 02:00
        Aliases= {}"""
        secs = await self._stamp_to_sec(ctx, timestamp)
        state = self.get_state(ctx.guild)
        voice = ctx.voice_client
        duration = state.now_playing.duration
        if secs is None:
            logging.info("invalid seek timestamp")
            await ctx.send("invalid timestamp")
        else:
            if secs > duration:
                logging.info("seek timestamp too long")
                await ctx.send("Timestamp is longer than the song dummy")
            else:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(source=state.now_playing.stream_url,
                                           before_options='-ss ' + str(timestamp) +
                                                          ' -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
                    volume=state.volume
                )
                song = state.now_playing
                song.seek = source
                state.playlist.insert(0, song)
                voice.stop()

    @staticmethod
    async def _stamp_to_sec(ctx, timestamp):
        parts = timestamp.split(":")
        if len(parts) < 1:
            await ctx.send("Invalid timestamp")
        else:

            values = (1, 60, 60 * 60, 60 * 60 * 24)

            secs = 0
            for i in range(len(parts)):
                try:
                    v = int(parts[i])
                except:
                    continue

                j = len(parts) - i - 1
                if j >= len(values):  # If I don't have a conversion from this to seconds
                    continue

                secs += v * values[j]
            is_digit = True
            for string in parts:
                if not str.isdigit(string):
                    is_digit = False
            if is_digit:
                return secs
            else:
                return None

    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='loop', aliases=['looping'])
    async def loop(self, ctx, *args):
        """Displays looping status, change status by passing "song", "queue" or "stop" for desired status
        Aliases= {looping}"""
        state = self.get_state(ctx.guild)
        if len(args) == 0:
            if state.looping is None:
                await ctx.send("not currently looping")
            else:
                await ctx.send("currently looping: " + str(state.looping))
        elif args[0] == "queue" or args[0] == "q":
            state.looping = "queue"
            await ctx.send("now looping this queue")
        elif args[0] == "song" or args[0] == "s":
            state.looping = "song"
            await ctx.send("now looping this song")
        elif args[0] == "none" or args[0] == "stop" or args[0] == "off":
            state.looping = None
            await ctx.send("no longer looping")
        else:
            await ctx.send("invalid argument")

    @commands.guild_only()
    @commands.check(in_voice)
    @commands.command(pass_context=True, name='playlist', aliases=['pl'])
    async def playlist(self, ctx, *args):
        """Takes a youtube or Spotify playlist link and add it to the queue (Spotify playlists limited to first 100)
        Aliases= {pl}"""
        queries = []
        if len(args) == 0:
            await ctx.send("No url given")
        else:
            pid = None
            url = utils.argument_concat(args)
            if not utils.url_validation(url):
                await ctx.send("invalid url")
                return
            if "spotify" in url:
                logging.info("spotify playlist")
                try:
                    pid = url.split("playlist/", 1)[1]
                    pid = pid.split("?si=", 1)[0]
                    logging.info("pid = " + pid)
                except:
                    await ctx.send("Error handling url, make sure it's the right type")
                    return
                try:
                    result = self.spot.playlist_tracks(playlist_id=pid, fields="items(track(name, artists))")
                except:
                    await ctx.send("There was an error processing your playlist")
                    return
                for track in result["items"]:
                    query = track['track']['artists'][0]['name'] + " " + track['track']['name']
                    queries.append(query)
            elif "youtube" in url:
                logging.info("yt playlist")
                ytdl_opts = {
                    "default_search": "auto",
                    "format": "bestaudio/best",
                    "quiet": True,
                    "extract_flat": "in_playlist",
                }
                with ytdl.YoutubeDL(ytdl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if "_type" in info and info["_type"] == "playlist":
                        pid = info["title"]
                        for video in info['entries']:

                            if not video:
                                logging.warning("ERROR: unable to get video info, continuing")
                                continue
                            else:
                                queries.append("https://www.youtube.com/watch?v=" + video["url"])
                    else:
                        logging.warning("url is not a yt playlist")
                        await ctx.send("That's not a playlist!")
                        return

            await ctx.send("adding playlist: " + pid + " to queue")
            for query in queries:
                try:
                    await self._play(ctx, query, True)
                    await asyncio.sleep(1)
                except:
                    logging.warning("playlist query error")
                    continue
            await ctx.send("Playlist added!")
