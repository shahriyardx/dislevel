from typing import Union

from asyncpg.pool import Pool
from databases import Database
from discord import Member
from discord.ext import commands, tasks
from typing_extensions import Literal

from .utils import prepare_db

from ._db_adapter import DbAdapter


class Leveling(commands.Cog):
    """
    Leveling commands
    """

    def __init__(
        self,
        bot: Union[commands.Bot, commands.AutoShardedBot],
        database: Union[Database, Pool],
        driver: Literal["asyncpg", "databases"],
    ):
        self.bot = bot

        if driver == "asyncpg":
            self.database = DbAdapter(database)
        else:
            self.database = database
        
        self.prepare_database.start()
        
    @tasks.loop(count=1)
    async def prepare_database(self):
        await prepare_db(self.database)

    @commands.command()
    async def rank(self, ctx: commands.Context, member: Member=None):
        """Check rank of yourself or a member"""
        if not member:
            member = ctx.author
        
        await ctx.send(f'Checking rank of {member}')
