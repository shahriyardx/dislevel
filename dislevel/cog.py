from discord.ext import commands
from typing_extensions import Literal

from ._db_adapter import DbAdapter


class Leveling(commands.Cog):
    """
    Leveling commands
    """

    def __init__(self, bot, database, driver: Literal["asyngpg", "databases"]):
        self.bot = bot

        if driver == "asyncpg":
            self.database = DbAdapter(database)
        else:
            self.database = database
