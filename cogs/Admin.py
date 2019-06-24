import discord
from discord.ext import commands
import config
import json


def setup(bot):
    bot.add_cog(Admin(bot))


class Admin(commands.Cog):
    """Cog for Admin tools and settings"""

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(pass_context=True, name="reset_settings", aliases=["rs"])
    async def reset_settings(self, ctx):
        """Resets the server's settings to the default values"""
        settings = config.load_settings()
        settings['guilds'][str(ctx.guild.id)] = {
            "leveling": True,
            "welcome": "Welcome to the server!",
            "goodbye": "You will be missed!",
            "warn_kick": 3,
            "warn_ban": 5,
            "max_volume": 250
        }
        with open("./settings.json", "w") as f:
            json.dump(settings, f)
        await ctx.send("Settings have been reset to default!")
