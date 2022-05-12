from typing import Union

from easy_pil.utils import run_in_executor
from nextcord import File, Member
from nextcord.ext import commands

from .card import get_card
from .utils import get_member_data, get_member_position


class Leveling(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot

    @commands.command()
    async def rank(self, ctx: commands.Context, *, member: Member = None):
        """Check rank of a user"""
        if not member:
            member = ctx.author

        user_data = await get_member_data(self.bot, member.id, ctx.guild.id)
        user_data["position"] = await get_member_position(
            self.bot, member.id, ctx.guild.id
        )
        user_data["profile_image"] = str(member.display_avatar.url)
        user_data["name"] = str(member).split("#")[0]
        user_data["descriminator"] = str(member).split("#")[1]
        
        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Leveling(bot))
