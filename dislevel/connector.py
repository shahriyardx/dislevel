import os

from typing_extensions import Literal

from ._db_adapter import DbAdapter
from .utils import prepare_db


async def init_dislevel(
    bot,
    database,
    driver: Literal["asyncpg", "databases"] = "databases",
):
    if driver == "asyncpg":
        database = DbAdapter(database)
    else:
        database = database

    bot.dislevel_database = database
    await prepare_db(database)

    os.environ[
        "DISLEVEL_LEADERBOARD_ICON_DEFAULT"
    ] = "https://cdn.discordapp.com/attachments/776345413132877854/974390375026401320/360_F_385427790_M4qA77J7nYgZCMP6Ezn9qo6PglF0j4mv-removebg-preview.png"

    os.environ["DISLEVEL_TABLE_DEFAULT"] = "dislevel_data"
