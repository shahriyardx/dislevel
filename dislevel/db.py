import os
import aiosqlite
import asyncpg


async def prepare_db(level_db):
    """Prepare database for leveling"""
    if level_db and isinstance(level_db, aiosqlite.Connection):
        await level_db.execute("""
            CREATE TABLE IF NOT EXISTS leveling(
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                exp INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1
            )
        """)
        await level_db.commit()
        return level_db

    elif level_db and isinstance(level_db, asyncpg.pool.Pool):
        await level_db.execute("""
            CREATE TABLE IF NOT EXISTS leveling(
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                guild_id BIGINT NOT NULL,
                exp BIGINT NOT NULL,
                level BIGINT NOT NULL
            )
        """)
        return level_db

    else:
        pass


async def update_data(row_id, exp, level, new_level, level_db):
    """Update specific row with given data"""
    if new_level > level:
        level = new_level
        
    if isinstance(level_db, aiosqlite.Connection):
        await level_db.execute("UPDATE leveling SET exp=?, level=? WHERE id=?", (exp, level, row_id))
        await level_db.commit()

    if isinstance(level_db, asyncpg.pool.Pool):
        await level_db.execute("UPDATE leveling SET exp=$1 level=$2 WHERE id=$3", exp, level, row_id)
    

async def get_data(user_id, guild_id, bot):
    """Get exp data"""
    if isinstance(bot.level_db, aiosqlite.Connection):
        user_data = await bot.level_db.execute("SELECT * FROM leveling WHERE user_id=? and guild_id=?", (user_id, guild_id))

        user_data = await user_data.fetchone()

        if not user_data:
            await bot.level_db.execute("INSERT INTO leveling(user_id, guild_id, exp) VALUES(?, ?, ?)", (user_id, guild_id, 0))
            await bot.level_db.commit()

            user_data = await bot.level_db.execute("SELECT * FROM leveling WHERE user_id=? and guild_id=?", (user_id, guild_id))
            user_data = await user_data.fetchone()

        guild_data = await bot.level_db.execute("SELECT * FROM leveling WHERE guild_id=? ORDER BY exp DESC", (guild_id,))
        data = await guild_data.fetchall()
        position = 0
        for row in data:
            position += 1
            if row[1] == user_data[1]:
                break

        user_data = [x for x in user_data]
        user_data.append(position)
        return user_data

    elif isinstance(bot.level_db, asyncpg.pool.Pool):
        user_data = await bot.level_db.fetchrow("SELECT * FROM leveling WHERE user_id=$1 and guild_id=$2", user_id, guild_id)
        if not user_data:
            await bot.level_db.execute("INSERT INTO leveling(user_id, guild_id, exp) VALUES($1, $2, $3)", user_id, guild_id, 0)
            user_data = await bot.level_db.fetchrow("SELECT * FROM leveling WHERE user_id=$1 and guild_id=$2", user_id, guild_id)

        guild_data = await bot.level_db.fetch("SELECT * FROM leveling WHERE guild_id=$1 ORDER BY exp DESC", guild_id)
        position = 0
        for row in guild_data:
            position += 1
            if row['user_id'] == user_data['user_id']:
                break

        data = [
            user_data['id'],
            user_data['user_id'],
            user_data['guild_id'],
            user_data['exp'],
            user_data['level'],
            position
        ]

        return data
    else:
        raise ValueError('Unsupported database config. Either user SQLite (aiosqlite) or PostgreSQL (asyncpg)')


async def increase_xp(message, bot, rate=5):
    await prepare_db(bot.level_db)
    user_data = await get_data(message.author.id, message.guild.id, bot)
    if user_data:
        exp = user_data[3] + rate
        level = user_data[4]
        new_level = int(exp ** (1 / 5))

        await update_data(user_data[0], exp, level, new_level, bot.level_db)


async def get_user_data(member, bot):
    await prepare_db(bot.level_db)
    data = await get_data(member.id, member.guild.id, bot)
    user_data = {
        "user_id": data[1],
        "guild_id": data[2],
        "current_user_exp": data[3],
        "current_level_min_xp": data[4] ** 5,
        "xp_required_for_next_level": (data[4] + 1) ** 5,
        "xp_required": ((data[4] + 1) ** 5) - data[3],
        "level": data[4],
        "position": data[5]
    }

    return user_data
