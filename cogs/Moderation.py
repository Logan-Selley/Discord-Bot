import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import asyncio
import config
import json
import logging

cfg = config.load_config()


def setup(bot):
    bot.add_cog(Moderation(bot, cfg))


class Moderation(commands.Cog):
    """Cog for moderator tools"""

    def __init__(self, bot, cfg):
        self.bot = bot
        self.cfg = cfg

    @commands.guild_only()
    @commands.command(pass_context=True, name="kick", aliases=[])
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        """Kicks the given member for the given reason
        aliases= {}"""
        if member is None:
            await ctx.send("You need to give me someone to kick")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot kick yourself")
            return
        elif member == ctx.guild.owner:
            await ctx.send("You can't kick my boss!")
            return
        elif member == self.bot.user:
            await ctx.send("Rude!")
            return
        if reason is None:
            reason = "For being a jerk!"
        message = f"You have been kicked from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.kick(member)
        await ctx.channel.send(f"{member.display_name} was kicked!")
        logging.warning(f"{member} was kicked!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="ban", aliases=[])
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        """Bans the given member for the given reason
        aliases= {}"""
        if member is None:
            await ctx.send("You need to give me someone to ban")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot ban yourself")
            return
        elif member == ctx.guild.owner:
            await ctx.send("You can't ban my boss!")
            return
        elif member == self.bot.user:
            await ctx.send("Rude!")
            return
        if reason is None:
            reason = "For being a jerk!"
        message = f"You have been banned from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.ban(member)
        await ctx.channel.send(f"{member.display_name} was banned!")
        logging.warning(f"{member} was banned!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="mute", aliases=[])
    @has_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.User = None, *, reason=None):
        """Mutes the given member for the reason given
        aliases= {}"""
        if member is None:
            await ctx.send("You need to give me someone to mute")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot mute yourself")
            return
        elif member == ctx.guild.owner:
            await ctx.send("You can't mute my boss!")
            return
        elif member == self.bot.user:
            await ctx.send("Rude!")
            return
        if reason is None:
            reason = "For being a jerk!"
        message = f"You have been muted from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.mute(member)
        await ctx.channel.send(f"{member.display_name} was muted!")
        logging.warning(f"{member} was muted!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="deafen", aliases=[])
    @has_permissions(mute_members=True)
    async def deafen(self, ctx, member: discord.User = None, *, reason=None):
        """Deafens the given member for the reason given
        aliases= {}"""
        if member is None:
            await ctx.send("You need to give me someone to deafen")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot deafen yourself")
            return
        elif member == ctx.guild.owner:
            await ctx.send("You can't deafen my boss!")
            return
        elif member == self.bot.user:
            await ctx.send("Rude!")
            return
        if reason is None:
            reason = "For being a jerk!"
        message = f"You have been deafened from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.mute(member)
        await ctx.channel.send(f"{member.display_name} was deafened!")
        logging.warning(f"{member} was deafened!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="prune", aliases=["pr"])
    @has_permissions(manage_messages=True)
    async def prune(self, ctx, count: int = None, member: discord.User = None):
        """Deletes the last (given number) of messages up to 100
        pass an @user to delete messages only from given user
        aliases= {pr}"""

        def check_user(m):
            return m.author == member
        if count is None:
            await ctx.send("You need to tell me how many messages to delete!")
            return
        if count > 100:
            count = 100
        if member is None:
            await ctx.channel.purge(limit=count)
            await ctx.send("Deleted the last " + str(count) + " messages!")
        else:
            await ctx.channel.purge(limit=count, check=check_user)
            await ctx.send("Deleted the last " + str(count) + " messages by " + str(member.display_name) + "!")
        logging.info(str(count) + " messages pruned by " + str(member))

    @commands.guild_only()
    @commands.command(pass_context=True, name="warn", aliases=[])
    @has_permissions(manage_roles=True, ban_members=True)
    async def warn(self, ctx, user: discord.User, *reason: str):
        """Function to log warnings/offenses, just pass the username, and reason for warning
        aliases= {}"""
        report = config.load_warns()
        if not reason:
            await ctx.send("Please provide a reason")
            return
        reason = ' '.join(reason)
        for guild in report['guilds']:
            if guild['id'] == ctx.guild.id:
                this_guild = report['guilds'].index(guild)
                break
        else:
            report['guilds'].append({
                'id': ctx.guild.id,
                'users': []
            })
            this_guild = len(report['guilds']) - 1
        for current_user in report['guilds'][this_guild]['users']:
            if current_user['id'] == user.id:
                current_user['reasons'].append(reason)
                break
        else:
            report['guilds'][this_guild]['users'].append({
                'id': user.id,
                'reasons': [reason, ]
            })
        with open('warnings.json', 'w+') as f:
            json.dump(report, f)
        await ctx.send(str(user.display_name) + " has been warned for: " + reason)
        logging.warning(f"{user} was warned!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="warnings", aliases=[])
    @has_permissions(manage_roles=True, ban_members=True)
    async def warnings(self, ctx, user: discord.User = None):
        """Function to retrieve the warnings of the given user
        aliases= {}"""
        if user is None:
            await ctx.send("you have to give me a user to get their warnings!")
            return
        report = config.load_warns()
        for guild in report['guilds']:
            if guild['id'] == ctx.guild.id:
                this_guild = report['guilds'].index(guild)
                break
        else:
            await ctx.send(f"{user.name} has never been warned")
            return
        for current_user in report['guilds'][this_guild]['users']:
            if user.name == current_user['id']:
                await ctx.send(f"{user.display_name} has been reported {len(current_user['reasons'])} times : "
                               f"{','.join(current_user['reasons'])}")
                break
        else:
            await ctx.send(f"{user.name} has never been warned")

    @commands.guild_only()
    @commands.command(pass_context=True, name="remove_warns", aliases=[])
    @has_permissions(manage_roles=True, ban_members=True)
    async def remove_warns(self, ctx, user: discord.User = None):
        """Function to remove all of a user's warns
        aliases= {}"""
        if user is None:
            await ctx.send("you have to give me a user to remove their warnings!")
            return
        report = config.load_warns()
        for guild in report['guilds']:
            if guild['id'] == ctx.guild.id:
                this_guild = report['guilds'].index(guild)
                break
        else:
            await ctx.send(f"{user.name} has never been warned")
            return
        for current_user in report['guilds'][this_guild]['users']:
            if user.name == current_user['id']:
                current_user['reasons'] = []
                await ctx.send(f"{user.display_name} has had all warnings removed")
                with open('warnings.json', 'w+') as f:
                    json.dump(report, f)
                logging.warning(str(user) + " had all warnings removed!")
                break
        else:
            await ctx.send(f"{user.display_name} has never been warned")

    @commands.guild_only()
    @commands.command(pass_context=True, name="soft_ban", aliases=[])
    @has_permissions(ban_members=True)
    async def soft_ban(self, ctx, member: discord.User = None, *, reason=None):
        """Bans the given member for the given reason and immediately unbans them
        aliases= {}"""
        if member is None:
            await ctx.send("You need to give me someone to soft ban")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot soft ban yourself")
            return
        elif member == ctx.guild.owner:
            await ctx.send("You can't soft ban my boss!")
            return
        elif member == self.bot.user:
            await ctx.send("Rude!")
            return
        if reason is None:
            reason = "For being a jerk!"
        message = f"You have been soft banned from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.ban(member)
        await ctx.guild.unban(member)
        await ctx.channel.send(f"{member.display_name} was soft banned!")
        logging.warning(f"{member.display_name} was soft banned!")
