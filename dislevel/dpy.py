from typing import Union

from easy_pil.utils import run_in_executor
from discord import Embed, File, Member
from discord.ext import commands

from ._types import DbType
from .card import get_card
from .utils import (
    LevelingTable,
    get_leaderboard_data,
    get_member_data,
    get_member_position,
    set_bg_image,
)


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

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx: commands.Context):
        """See the server leaderboard"""
        leaderboard_data = await get_leaderboard_data(self.bot, ctx.guild.id)

        embed = Embed(title=f"Leaderboard", description="")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/776345413132877854/974390375026401320/360_F_385427790_M4qA77J7nYgZCMP6Ezn9qo6PglF0j4mv-removebg-preview.png"
        )

        position = 0
        for data in leaderboard_data:
            member = None
            if self.bot.intents.members:
                member = ctx.guild.get_member(data["member_id"])
            else:
                member = await ctx.guild.fetch_member(data["member_id"])

            if member:
                position += 1
                embed.description += f"{position}. {member.mention} - {data['xp']}"

        await ctx.send(embed=embed)

    @commands.command()
    async def setbg(self, ctx: commands.Context, *, url: str):
        """Set image of your card bg."""
        await set_bg_image(self.bot, ctx.author.id, ctx.guild.id, url)
        await ctx.send("Background image has been updated")

    @commands.command()
    async def resetbg(self, ctx: commands.Context):
        """Set image of your card bg."""
        await set_bg_image(self.bot, ctx.author.id, ctx.guild.id, "")
        await ctx.send("Background image has been set to default")


async def setup(bot):
    await bot.add_cog(Leveling(bot))
