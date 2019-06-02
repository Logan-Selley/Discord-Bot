import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import asyncio


def setup(bot):
    bot.add_cog(Moderation(bot))


class Moderation(commands.Cog):
    """Cog for moderator tools"""

    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(pass_context=True, name="kick", aliases=[])
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
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
        await ctx.channel.send(f"{member} was kicked!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="ban", aliases=[])
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
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
        await ctx.guild.kick(member)
        await ctx.channel.send(f"{member} was banned!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="mute", aliases=[])
    @has_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.Member = None, *, reason=None):
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
        await ctx.channel.send(f"{member} was muted!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="deafen", aliases=[])
    @has_permissions(mute_members=True)
    async def deafen(self, ctx, member: discord.Member = None, *, reason=None):
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
        await ctx.channel.send(f"{member} was deafened!")

    @commands.guild_only()
    @commands.command(pass_context=True, name="prune", aliases=["pr"])
    @has_permissions(manage_messages=True)
    async def prune(self, ctx, count: int = None, member: discord.Member = None):
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
            await ctx.send("Deleted the last " + str(count) + " messages by " + str(member) + "!")


