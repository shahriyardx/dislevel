from typing import Union

from asyncpg.pool import Pool
from databases import Database

from ._db_adapter import DbAdapter

DbType = Union[Database, Pool, DbAdapter]

__all__ = ["DbType"]
