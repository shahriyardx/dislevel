import os
from typing import Optional, Union

from discord import Embed, File, Interaction, Member, app_commands
from discord.ext import commands
from easy_pil.utils import run_in_executor

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

    @app_commands.command(description="Check rank of a user")
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

        await interaction.response.send_message(file=file)

    @app_commands.command(description="See the server leaderboard")
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
                embed.description += f"{position}. {member.mention} - {data['xp']}"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Set image of your card bg")
    async def setbg(self, interaction: Interaction, *, url: str):
        """Set image of your card bg"""
        await set_bg_image(self.bot, interaction.user.id, interaction.guild.id, url)
        await interaction.response.send_message("Background image has been updated")

    @app_commands.command(description="Reset image of your card bg")
    async def resetbg(self, interaction: Interaction):
        """Reset image of your card bg"""
        await set_bg_image(self.bot, interaction.user.id, interaction.guild.id, "")
        await interaction.response.send_message(
            "Background image has been set to default"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelingSlash(bot))
