import re


class DbAdapter:
    """
    An adapter that allows databases type queries in asyncpg
    """

    def __init__(self, pool):
        self.pool = pool

    def get_data(self, query, values: dict = dict()):
        if not values:
            return [query, []]

        items = []
        vars = re.findall(r"(:[a-zA-Z_]+)", query)

        for index, match in enumerate(vars):
            var = match[1:]
            items.append(values[var])
            query = query.replace(match, f"${index+1}")

        return [query, items]

    async def fetch_one(self, query: str, values: dict = dict()):
        nq, nv = self.get_data(query, values)

        async with self.pool.acquire() as con:
            data = await con.fetchrow(nq, *nv)
            return data

    async def fetch_all(self, query: str, values: dict = dict()):
        nq, nv = self.get_data(query, values)
        async with self.pool.acquire() as con:
            data = await con.fetch(nq, *nv)
            return data

    async def fetch_val(self, query: str, values: dict = dict()):
        nq, nv = self.get_data(query, values)
        async with self.pool.acquire() as con:
            data = await con.fetchval(nq, *nv)
            return data

    async def execute(self, query: str, values: dict = dict()):
        nq, nv = self.get_data(query, values)
        async with self.pool.acquire() as con:
            await con.execute(nq, *nv)
