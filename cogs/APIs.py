from discord.ext import commands
import config


cfg = config.load_config()


def setup(bot):
    bot.add_cog(APIs(bot, cfg))


class APIs(commands.Cog):
    """Commands for various integrated APIs"""
    def __init__(self, bot, cfg):
        self.bot = bot
        self.config = cfg
