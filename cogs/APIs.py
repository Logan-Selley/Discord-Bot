from discord.ext import commands
import config
import strawpoll
import pybitly
import giphy_client
import soundcloud
import praw
import meetup
import pyimgur
import forecastio
from utils import argument_concat
import geopy
import asyncio


cfg = config.load_config()


def setup(bot):
    bot.add_cog(APIs(bot, cfg))


class APIs(commands.Cog):
    """Commands for various integrated APIs"""
    def __init__(self, bot, cfg):
        self.bot = bot
        self.config = cfg[__name__.split(".")[-1]]

    @commands.command(pass_context=True, name="weather", aliases=["w"])
    async def weather(self, ctx, *location: str, type=None):
        """Uses the Dark Sky API to get weather data for the given location, coordinates are accessed using geopy
        aliases= {w}"""
        key = self.config["forcastio"]
        if len(location) == 0:
            await ctx.send("You need to give me a location!")
            raise commands.MissingRequiredArgument
        local = argument_concat(location)
        geolocator = geopy.Nominatim(user_agent="Very Sad Intern")
        loc = geolocator.geocode(local)
        if loc is None:
            await ctx.send("I couldn't get a geocode for that location!")
            return
        lat = loc.latitude
        long = loc.longitude
        forecast = forecastio.load_forecast(key, lat, long)
        weather = forecast.json['currently']
        await ctx.send(loc.address + ": " + weather['summary'] + " at " + str(weather['temperature'])
                       + " degrees fahrenheit")
