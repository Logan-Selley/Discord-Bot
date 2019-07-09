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

    @commands.guild_only()
    @commands.command(pass_context=True, name="profile", aliases=[])
    async def profile(self, ctx, member: discord.Member = None):
        """Displays the given member's info or the callers info if no member is given
        aliases= {pr}"""

    @commands.guild_only()
    @commands.command(pass_context=True, name="avatar", aliases=[])
    async def avatar(self, ctx, user: discord.User = None):
        """Displays the given user's or the caller's avatar
        aliases={}"""
        if user is None:
            user = ctx.author
        avatar = user.avatar_url
        embed = discord.Embed(
            title=user.name + "'s Avatar:",
            color=discord.Colour.purple()
        )
        embed.set_image(url=avatar)
        await ctx.send("", embed=embed)


    @commands.guild_only()
    @commands.command(pass_context=True, name="server_info", aliases=["si"])
    async def server_info(self, ctx):
        """Displays the info and stats of the current server
        aliases={si}"""
        guild = ctx.guild
        boost_count = guild.premium_subscription_count
        region = str(guild.region)
        channels = len(guild.channels)
        vc = len(guild.voice_channels)
        text_channels = len(guild.text_channels)
        emoji_limit = guild.emoji_limit
        bitrate = guild.bitrate_limit
        filesize = guild.filesize_limit
        members = str(len(guild.members))
        owner = guild.owner.name
        icon = guild.icon_url
        roles = len(guild.roles)
        banned = len(await guild.bans())
        invites = len(await guild.invites())
        created = str(guild.created_at)
        embed = discord.Embed(
            title=guild.name,
            description="Server Info:",
            color=discord.Colour.purple()
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Owner: ", value=owner)
        embed.add_field(name="Region: ", value=region)
        embed.add_field(name="created at: ", value=created)
        embed.add_field(name="Boost count: ", value=boost_count)
        embed.add_field(name="Members: ", value=members)
        embed.add_field(name="Roles:", value=str(roles))
        embed.add_field(name="Channels:", value=str(channels))
        embed.add_field(name="Text Channels:", value=str(text_channels))
        embed.add_field(name="Voice Channels:", value=str(vc))
        embed.add_field(name="Emoji Limit:", value=str(emoji_limit))
        embed.add_field(name="Max Bitrate:", value=bitrate)
        embed.add_field(name="Max Filesize:", value=filesize)
        embed.add_field(name="Banned Members:", value=str(banned))
        embed.add_field(name="Active Invites:", value=str(invites))
        await ctx.send("", embed=embed)

    @commands.guild_only()
    @commands.command(pass_context=True, name="settings")
    async def settings(self, ctx):
        """Displays the servers settings for me!
        aliases= {}"""
        settings = config.load_settings()
        guild = ctx.guild.id
        embed = discord.Embed(
            title=ctx.guild.name + " bot settings!",
            description="My settings for this server!",
            color=discord.Colour.purple()
        )
        embed.add_field(name="Prefix", value=settings['guilds'][str(guild)]['prefix'])
        embed.add_field(name="Max Volume", value=str(settings['guilds'][str(guild)]['max_volume']))
        embed.add_field(name="Leveling system", value=settings['guilds'][str(guild)]['leveling'])
        embed.add_field(name="Welcome Message", value=settings['guilds'][str(guild)]['welcome'])
        embed.add_field(name="Goodbye Message", value=settings['guilds'][str(guild)]['goodbye'])
        embed.add_field(name="Warns until kick", value=str(settings['guilds'][str(guild)]['warn_kick']))
        embed.add_field(name="Warns until ban", value=str(settings['guilds'][str(guild)]['warn_ban']))
        await ctx.send("", embed=embed)
