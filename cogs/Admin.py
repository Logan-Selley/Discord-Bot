import discord
from discord.ext import commands
import config
import json
import bot


def setup(bot):
    bot.add_cog(Admin(bot))


class Admin(commands.Cog):
    """Cog for Admin tools and settings"""

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="reset_settings", aliases=["rs"])
    async def reset_settings(self, ctx):
        """Resets the server's settings to the default values
        aliases={rs}"""
        settings = config.load_settings()
        settings['guilds'][str(ctx.guild.id)] = {
            "prefix": "!",
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

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="toggle_levels", aliases=["tl"])
    async def toggle_levels(self, ctx):
        """Toggles whether the server keeps track of user levels
        aliases={tl}"""
        settings = config.load_settings()
        guild = ctx.guild.id
        if settings['guilds'][str(guild)]['leveling'] is True:
            settings['guilds'][str(guild)]['leveling'] = False
            await ctx.send("leveling disabled!")
        else:
            settings['guilds'][str(guild)]['leveling'] = True
            await ctx.send("leveling enabled!")
        with open("./settings.json", "w") as f:
            json.dump(settings, f)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="change_prefix", aliases=["cp"])
    async def change_prefix(self, ctx, prefix="!"):
        settings = config.load_settings()
        guild = ctx.guild.id
        settings['guilds'][str(guild)]['prefix'] = prefix
        await ctx.send("My prefix for this server has been changed to: " + prefix)
        with open("./settings.json", "w") as f:
            json.dump(settings, f)
        bot.bot.command_prefix = bot.prefix(bot.bot, ctx.message)