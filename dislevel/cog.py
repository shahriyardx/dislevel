import os
from discord.ext import commands
from .db import get_user_data, add_level_role, remove_level_role
from .card import get_card
from easy_pil import run_in_executor
from discord import Member, Role, File


from databases import Database


class Leveling(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.level_db = Database("sqlite:///leveling.db")
        self.bot.level_db_prepared = False

    @commands.command()
    async def rank(self, ctx, member: Member = None):
        if not member:
            member = ctx.author

        user_data = await get_user_data(member, self.bot)
        user_data["profile_image"] = str(member.avatar_url)
        user_data["name"] = str(member).split("#")[0]
        user_data["descriminator"] = str(member).split("#")[1]

        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await ctx.send(file=file)

    @commands.group(invoke_without_comamnd=True)
    async def levelrole(self, ctx):
        pass

    @levelrole.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, level: int, role: Role):
        msg = await add_level_role(self.bot, ctx.guild.id, level, role.id)
        await ctx.send(msg)

    @levelrole.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, level: int):
        msg = await remove_level_role(self.bot, ctx.guild.id, level)
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Leveling(bot))
