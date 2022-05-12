from typing import Union

from ._types import DbType

LevelingTable: str = "dislevel_data"


async def prepare_db(database: DbType) -> None:
    """Prepares the database for leveling"""
    try:
        await database.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {LevelingTable}(
                id          BIGSERIAL PRIMARY KEY,
                member_id   BIGINT NOT NULL,
                guild_id    BIGINT NOT NULL,
                xp          BIGINT NOT NULL DEFAULT 1,
                level       BIGINT NOT NULL DEFAULT 1,
                bg_image    TEXT NULL
            )
            """
        )
    except Exception as e:
        print(e)


def get_percentage(data):
    user_xp = data["xp"]
    user_level = data["level"]
    min_xp = user_level**5
    next_level_xp = (user_level + 1) ** 5
    xp_required = next_level_xp - min_xp
    xp_have = user_xp - min_xp

    data["percentage"] = (100 * xp_have) / xp_required
    data["next_level_xp"] = next_level_xp

    return data


async def get_member_data(bot, member_id: int, guild_id: int) -> Union[dict, None]:
    """Returns data of an member"""
    database: DbType = bot.dislevel_database
    data = await database.fetch_one(
        f"""
        SELECT  * 
        FROM    {LevelingTable} 
        WHERE   guild_id = :guild_id 
        AND     member_id = :member_id
        """,
        {"guild_id": guild_id, "member_id": member_id},
    )

    if not data:
        return None

    return get_percentage(dict(data))


async def get_leaderboard_data(bot, guild_id: int):
    """Get a guild's leaderboard data"""
    database: DbType = bot.dislevel_database
    data = await database.fetch_all(
        f"""
        SELECT   member_id, xp
        FROM     {LevelingTable}
        WHERE    guild_id = :guild_id
        ORDER BY xp
        DESC
        LIMIT 10
        """,
        {"guild_id": guild_id},
    )

    guild_data = [dict(row) for row in data]
    return guild_data


async def get_member_position(bot, member_id: int, guild_id: int):
    """Get position of a member"""
    database: DbType = bot.dislevel_database
    data = await database.fetch_all(
        f"""SELECT  *
             FROM   {LevelingTable} 
            WHERE   guild_id = :guild_id 
         ORDER BY   xp 
             DESC
        """,
        {"guild_id": guild_id},
    )

    position = 0
    for row in data:
        position += 1
        if member_id == row["member_id"]:
            break

    return position


async def update_xp(bot, member_id: int, guild_id: int, amount: int = 0) -> None:
    """Increate xp of a member"""
    database: DbType = bot.dislevel_database
    user_data = await get_member_data(bot, member_id, guild_id)

    if user_data:
        level = user_data["level"]
        new_xp = user_data["xp"] + amount
        new_level = int(new_xp ** (1 / 5))

        await database.execute(
            f"""
            UPDATE  {LevelingTable} 
                SET  xp = :xp, 
                    level = :level 
                WHERE  member_id = :member_id 
                AND  guild_id = :guild_id
            """,
            {
                "xp": new_xp,
                "level": new_level,
                "guild_id": guild_id,
                "member_id": member_id,
            },
        )

        if new_level > level:
            bot.dispatch(
                "dislevel_levelup",
                guild_id=guild_id,
                member_id=member_id,
                level=new_level,
            )

    else:
        level = int(amount ** (1 / 5))
        await database.execute(
            f"""
            INSERT  INTO {LevelingTable}
                    (member_id, guild_id, xp, level) 
            VALUES  (:member_id, :guild_id, :xp, :level)
            """,
            {
                "xp": amount,
                "level": level,
                "guild_id": guild_id,
                "member_id": member_id,
            },
        )


async def delete_member_data(bot, member_id: int, guild_id: int) -> None:
    """Deletes a member's data. Usefull when you want to delete member's data if they leave server"""
    database: DbType = bot.dislevel_database
    await database.executec(
        f"""
        DELETE  FROM {LevelingTable}
         WHERE  member_id = :member_id
           AND  guild_id = :guild_id
        """,
        {
            "guild_id": guild_id,
            "member_id": member_id,
        },
    )


async def set_bg_image(bot, member_id: int, guild_id: int, url) -> None:
    """Set bg image"""
    database: DbType = bot.dislevel_database
    await database.execute(
        f"""
        UPDATE  {LevelingTable}
        SET     bg_image = :bg_image
        WHERE   guild_id = :guild_id
        AND     member_id = :member_id 
        """,
        {"bg_image": url, "guild_id": guild_id, "member_id": member_id},
    )
