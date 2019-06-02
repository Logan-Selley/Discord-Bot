import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure
import sys
import traceback


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))


class CommandErrorHandler(commands.Cog):
    """Cog that fixes things when you fuck things up"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_command_error')
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        if isinstance(error, commands.MissingPermissions):
            text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
            await ctx.send(text)

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permission to do that!")

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You can't use that command yet!")

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me enough arguments for that command!")

        if isinstance(error, commands.TooManyArguments):
            await ctx.send("Woah!, Too much information!")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send("I don't know that command!")

        if isinstance(error, commands.ArgumentParsingError):
            await ctx.send("I'm not sure how to read the argument you gave me!")

        if isinstance(error, commands.BadArgument):
            await ctx.send("You gave me a bad argument! How am I supposed to work in these conditions!")

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                return await ctx.send('I could not find that member. Please try again.')

        # All other Errors not returned come here... And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
