import discord
from discord.ext import commands
import config

cfg = config.load_config()


def setup(bot):
    bot.add_cog(General(bot))


class General(commands.Cog):
    """General use commands that don't fit anywhere else"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='ping')
    async def ping(self, ctx):
        """Simple bot response command
        Aliases= {}"""
        await ctx.send('pong')

    @commands.command(pass_context=True, name='wink')
    async def wink(self, ctx):
        """Simple bot response command
        Aliases= {}"""
        await ctx.send('wonk')

    @commands.command(pass_context=True, name='pre', aliases=['prefix'])
    async def pre(self, ctx):
        """Displays the current command prefix
        Aliases= {prefix}"""
        await ctx.send('Current prefix: ' + cfg["prefix"])

    '''Written by Jared Newsom(AKA Jared M.F.)!'''

    @commands.command()
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help(self, ctx, *cog):
        """Gets all cogs and commands of mine."""
        try:
            halp = None
            if not cog:
                halp = discord.Embed(title='Cog Listing and Uncatergorized Commands',
                                     description='Use `!help *cog*` to find out more about them!\n'
                                                 '(BTW, the Cog Name Must Be in Title Case, Just Like this Sentence.)')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x, self.bot.cogs[x].__doc__)+'\n')
                halp.add_field(name='Cogs', value=cogs_desc[0:len(cogs_desc)-1], inline=False)
                cmds_desc = 'None '
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name, y.help)+'\n')
                halp.add_field(name='Uncatergorized Commands', value=cmds_desc[0:len(cmds_desc)-1], inline=False)
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('', embed=halp)
            else:
                if len(cog) > 1:
                    halp = discord.Embed(title='Error!', description='That is way too many cogs!',
                                         color=discord.Color.red())
                    await ctx.message.author.send('', embed=halp)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                halp = discord.Embed(title=cog[0]+' Command Listing',
                                                     description=self.bot.cogs[cog[0]].__doc__)
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        halp.add_field(name=c.name, value=c.help, inline=False)
                                found = True
                    if not found:
                        halp = discord.Embed(title='Error!', description='How do you even use "'+cog[0]+'"?',
                                             color=discord.Color.red())
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send('', embed=halp)
        except:
            pass