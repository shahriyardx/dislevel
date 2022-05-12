from typing import Union

from asyncpg.pool import Pool
from databases import Database
from discord.ext import commands
from typing_extensions import Literal

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
