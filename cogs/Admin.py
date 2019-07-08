import discord
from discord.ext import commands
import config
import json
import bot
import utils


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
        """Changes the server's command prefix to the given string
        aliases={cp}"""
        settings = config.load_settings()
        guild = ctx.guild.id
        settings['guilds'][str(guild)]['prefix'] = prefix
        await ctx.send("My prefix for this server has been changed to: " + prefix)
        with open("./settings.json", "w") as f:
            json.dump(settings, f)
        bot.bot.command_prefix = bot.prefix(bot.bot, ctx.message)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="max_volume", aliases=['mv'])
    async def max_volume(self, ctx, vol: int):
        """Changes the server's max volume to the given integer
        aliases={mv}"""
        settings = config.load_settings()
        guild = ctx.guild.id
        settings['guilds'][str(guild)]['max_volume'] = vol
        await ctx.send("Max volume for this server has been set to: " + str(vol))
        with open("./settings.json", "w") as f:
            json.dump(settings, f)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="change_welcome", aliases=['cw'])
    async def change_welcome(self, ctx, *welcome: str):
        """Changes the server's welcome message to the given string
        aliases={cw}"""
        settings = config.load_settings()
        guild = ctx.guild.id
        message = utils.argument_concat(welcome)
        settings['guilds'][str(guild)]['welcome'] = message
        await ctx.send("The welcome message for this server has been set to: " + message)
        with open("./settings.json", "w") as f:
            json.dump(settings, f)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="change_goodbye", aliases=['cgb'])
    async def change_goodbye(self, ctx, *goodbye: str):
        """Changes the server's welcome message to the given string
        aliases={cw}"""
        settings = config.load_settings()
        guild = ctx.guild.id
        message = utils.argument_concat(goodbye)
        settings['guilds'][str(guild)]['goodbye'] = message
        await ctx.send("The goodbye message for this server has been set to: " + message)
        with open("./settings.json", "w") as f:
            json.dump(settings, f)

