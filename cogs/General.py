import discord
from discord.ext import commands
import config
import random
import collections
import operator

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
        settings = config.load_settings()
        guild = ctx.guild.id
        await ctx.send('Current prefix: ' + settings['guilds'][str(guild)]['prefix'])

    '''Written by Jared Newsom(AKA Jared M.F.)!'''

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
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

    @commands.command(pass_context=True, name='coin', aliases=['coinflip', 'flip'])
    async def coin(self, ctx):
        """Has the bot flip a coin!
        aliases= {coinflip, flip}"""
        flip = random.randint(1, 2)
        if flip == 1:
            await ctx.send("You flipped heads!")
        else:
            await ctx.send("You flipped tails!")

    @commands.command(pass_context=True, name='roll', aliases=['diceroll', 'dice'])
    async def roll(self, ctx, sides: int = None):
        """Has the bot roll a dice with the given number of sides
        aliases= {diceroll, dice}"""
        if sides is None:
            await ctx.send("You have to tell me how many sides the die has!")
            return
        roll = random.randint(1, sides)
        await ctx.send("You rolled: " + str(roll))

    @commands.guild_only()
    @commands.command(pass_context=True, name='level', aliases=['lvl'])
    async def level(self, ctx, user: discord.User = None):
        """Display a user's progress to the next level or display the progress of the given user
        aliases= {lvl}"""
        settings = config.load_settings()
        if settings['guilds'][str(ctx.guild.id)]["leveling"] is True:
            guild = ctx.guild.id
            if user is None:
                id = ctx.author.id
                name = ctx.author.display_name
            else:
                id = user.id
                name = user.display_name
            xp = config.load_xp()
            exp = 0
            level = 0
            if str(guild) in xp['guilds']:
                if str(id) in xp['guilds'][str(guild)]:
                    exp = xp['guilds'][str(guild)][str(id)]['xp']
                    level = xp['guilds'][str(guild)][str(id)]['level']
            await ctx.send(name + " is currently level: " + str(level) + " with " + str(exp) + " experience!")
        else:
            await ctx.send("leveling is currently disabled on this server!")

    @commands.guild_only()
    @commands.command(pass_context=True, name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        """Display the top users for the current server
        aliases= {lb}"""
        settings = config.load_settings()
        if settings['guilds'][str(ctx.guild.id)]["leveling"] is True:
            guild = ctx.guild.id
            xp = config.load_xp()
            scores = {}
            if str(guild) in xp['guilds']:
                for user in xp['guilds'][str(guild)]:
                    scores.update({ctx.guild.get_member(int(user)).display_name: xp['guilds'][str(guild)][user]['xp']})
            sorted_scores = collections.OrderedDict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
            message = discord.Embed(title='Leaderboard', description=ctx.guild.name + "'s most active users")
            current_field = 1
            field_limit = 25
            for index, (key, value) in enumerate(sorted_scores.items()):
                if current_field <= field_limit:
                    message.add_field(name=str(index+1) + ": " + key,
                                      value="with: " + str(value) + " xp",
                                      inline=False)
                    current_field += 1
                else:
                    break
            await ctx.send('', embed=message)
        else:
            await ctx.send("leveling is currently disabled on this server!")
