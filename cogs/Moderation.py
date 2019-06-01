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
    @commands.command(pass_context=True, name="kick", aliases=["k"])
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, reason =None):
        """Kicks the given member for the given reason
        aliases= {k}"""
        if member is None:
            await ctx.send("You need to give me someone to kick")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot kick yourself")
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
    @commands.command(pass_context=True, name="ban", aliases=["b"])
    @has_permissions(kick_members=True)
    async def ban(self, ctx, member: discord.Member = None, reason=None):
        """Bans the given member for the given reason
        aliases= {b}"""
        if member is None:
            await ctx.send("You need to give me someone to ban")
            return
        elif member == ctx.message.author:
            await ctx.send("You cannot ban yourself")
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
    @commands.command(pass_context=True, name="prune", aliases=["pr"])
    @has_permissions(manage_messages=True)
    async def prune(self, ctx, count: int):
        """Deletes the last (given number) of messages up to 100
        aliases= {pr}"""
        messages = []
        print(count)
        if count is None:
            await ctx.send("You need to tell me how many messages to delete!")
            return
        if count > 100:
            count = 100
        async for x in ctx.channel.audit_logs(limit=count):
            messages.append(x)
        await self.bot.delete_messages(messages)
        await ctx.send("Deleted the last " + str(count) + " messages!")
