import os
from typing import Optional, Union

from easy_pil.utils import run_in_executor
from nextcord import Embed, File, Interaction, Member, slash_command
from nextcord.ext import commands

from ..card import get_card
from ..utils import (
    get_leaderboard_data,
    get_member_data,
    get_member_position,
    set_bg_image,
)


class LevelingSlash(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot

    @slash_command(description="Check rank of a user")
    async def rank(self, interaction: Interaction, *, member: Optional[Member]):
        """Check rank of a user"""
        if not member:
            member = interaction.user

        user_data = await get_member_data(self.bot, member.id, interaction.guild.id)
        user_data["position"] = await get_member_position(
            self.bot, member.id, interaction.guild.id
        )
        user_data["profile_image"] = str(member.display_avatar.url)
        user_data["name"] = str(member).split("#")[0]
        user_data["descriminator"] = str(member).split("#")[1]

        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await interaction.send(file=file)

    @slash_command(description="See the server leaderboard")
    async def leaderboard(self, interaction: Interaction):
        """See the server leaderboard"""
        leaderboard_data = await get_leaderboard_data(self.bot, interaction.guild.id)

        embed = Embed(title=f"Leaderboard", description="")
        embed.set_thumbnail(url=os.environ.get("DISLEVEL_LEADERBOARD_ICON"))

        position = 0
        for data in leaderboard_data:
            member = None
            if self.bot.intents.members:
                member = interaction.guild.get_member(data["member_id"])
            else:
                member = await interaction.guild.fetch_member(data["member_id"])

            if member:
                position += 1
                embed.description += f"{position}. {member.mention} - {data['xp']}\n"

        await interaction.send(embed=embed)

    @slash_command(description="Set image of your card bg")
    async def setbg(self, interaction: Interaction, *, url: str):
        """Set image of your card bg"""
        await set_bg_image(self.bot, interaction.user.id, interaction.guild.id, url)
        await interaction.send("Background image has been updated")

    @slash_command(description="Reset image of your card bg")
    async def resetbg(self, interaction: Interaction):
        """Reset image of your card bg"""
        await set_bg_image(self.bot, interaction.user.id, interaction.guild.id, "")
        await interaction.send("Background image has been set to default")


def setup(bot: commands.Bot):
    bot.add_cog(LevelingSlash(bot))
