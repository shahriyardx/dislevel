import os
import discord
from discord.ext import commands
from .db import (
    get_user_data,
    add_level_role,
    remove_level_role,
    get_level_roles,
    give_rep,
    get_leaderboard_data
)
from .card import get_card
from easy_pil import run_in_executor, load_image_async
from discord import Member, Role, File, Embed


from databases import Database


class Leveling(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.level_db = Database("sqlite:///leveling.db")
        self.bot.level_db_prepared = False

    @commands.command()
    async def rank(self, ctx, member: Member = None):
        """See rank."""
        if not member:
            member = ctx.author

        user_data = await get_user_data(member, self.bot)
        user_data["profile_image"] = str(member.avatar_url)
        user_data["name"] = str(member).split("#")[0]
        user_data["descriminator"] = str(member).split("#")[1]

        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await ctx.send(file=file)
    
    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Get leaderboard data"""
        data = await get_leaderboard_data(self.bot, ctx.guild.id)
        print(data)
        desc = ""
        pos = 0
        has_intent = self.bot.intents.members

        for row in data:
            if has_intent:
                user = ctx.guild.get_member(row[1])
            else:
                try:
                    user = await ctx.guild.fetch_member(row[1])
                except Exception as e:
                    print(e)
                    continue
            if not user:
                continue
            pos += 1
            desc += f"{pos}. {user.mention} | {row[3]}xp\n"
        
        embed = Embed(title="Leaderboard", description=desc)
        embed.set_thumbnail(url=str(ctx.guild.icon_url))

        await ctx.send(embed=embed)

    @commands.command()
    async def rep(self, ctx, member: Member):
        """Give reputation to a member"""
        if member.id == ctx.author.id:
            return await ctx.send("Can't give reputation to yourself.")

        await give_rep(self.bot, member)

        await ctx.send(f"{member.mention}'s reputation has been increased.")

    @commands.command()
    async def setbg(self, ctx, url: str):
        """Change your card background"""
        msg = await ctx.send("Verifying url...")
        try:
            await load_image_async(url)
            await self.bot.level_db.execute(
                "UPDATE leveling SET bg_image=:bg_image WHERE guild_id=:guild_id AND user_id=:user_id",
                {"bg_image": url, "guild_id": ctx.guild.id, "user_id": ctx.author.id},
            )
            await msg.edit(content="Background image has been set.")
        except Exception as e:
            print(e)
            await msg.edit(
                content="Unable to load image from provided link. Please provide a valid image url."
            )

    @commands.command()
    async def resetbg(self, ctx):
        """Reset your card background"""

        await self.bot.level_db.execute(
            "UPDATE leveling SET bg_image=:bg_image WHERE guild_id=:guild_id AND user_id=:user_id",
            {"bg_image": "", "guild_id": ctx.guild.id, "user_id": ctx.author.id},
        )
        await ctx.send("Background image has been reseted.")

    @commands.group(invoke_without_command=True)
    async def levelrole(self, ctx):
        """See all level roles."""
        roles = await get_level_roles(self.bot, ctx.guild)

        embed = Embed(title="Level Roles", description="")

        for level, role in roles.items():
            embed.description += f"{role.mention} - {level} \n"

        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.color = discord.Color.blurple()

        await ctx.send(embed=embed)

    @levelrole.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, level: int, role: Role):
        """Add a level role to a certain level"""
        msg = await add_level_role(self.bot, ctx.guild.id, level, role.id)
        await ctx.send(msg)

    @levelrole.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, level: int):
        """Remove a level role from a certain level"""
        msg = await remove_level_role(self.bot, ctx.guild.id, level)
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Leveling(bot))
