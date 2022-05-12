from ._db_adapter import DbAdapter
from asyncpg.pool import Pool
from databases import Database
from typing import Union


async def prepare_db(database: Union[Database, Pool, DbAdapter]):
    """Prepares the database for leveling"""
    await database.execute(
        """
            CREATE TABLE IF NOT EXISTS leveling(
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                guild_id BIGINT NOT NULL,
                exp BIGINT NOT NULL DEFAULT 1,
                level BIGINT NOT NULL DEFAULT 1,
                bg_image TEXT NULL
            )
        """
    )
    

async def get_member_data(database, guild_id: int, member_id):
    """Returns data of an member"""