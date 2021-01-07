from discord.ext import commands
from dislevel.db import get_user_data
from discord import Member
from disrank.generator import Generator
from functools import partial
import asyncio
import discord
import os


class Leveling(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.level_db = getattr(self.bot, os.getenv("DISLEVEL_DB_CONN"))
        self.bot._card_generator = Generator()

    def get_card(self, args):
        image = Generator().generate_profile(**args)
        return image

    @commands.command()
    async def rank(self, ctx, member: Member = None):
        if not member:
            member = ctx.author

        user_data = await get_user_data(member, self.bot)

        args = {
            'bg_image': '',
            'profile_image': str(member.avatar_url_as(format='png')),
            'level': user_data['level'],
            'current_xp': user_data['current_level_min_xp'],
            'user_xp': user_data['current_user_exp'],
            'next_xp': user_data['xp_required_for_next_level'],
            'user_position': user_data['position'],
            'user_name': str(member),
            'user_status': member.status.name,
        }

        func = partial(self.get_card, args)
        image = await asyncio.get_event_loop().run_in_executor(None, func)

        file = discord.File(fp=image, filename='image.png')
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Leveling(bot))
