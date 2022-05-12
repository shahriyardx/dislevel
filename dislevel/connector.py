from typing import Union

from asyncpg.pool import Pool
from databases import Database
from typing_extensions import Literal

from ._db_adapter import DbAdapter
from .utils import prepare_db


async def init_dislevel(
    bot,
    database: Union[Database, Pool],
    driver: Literal["asyncpg", "databases"] = "databases",
):
    if driver == "asyncpg":
        database = DbAdapter(database)
    else:
        database = database

    bot.dislevel_database = database
    await prepare_db(database)
