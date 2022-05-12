from ._types import DbType

LevelingTable: str = "dislevel_data"


async def prepare_db(database: DbType):
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


async def get_member_data(bot, member_id: int, guild_id: int):
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

    return dict(data)


async def update_xp(bot, member_id: int, guild_id: int, amount: int = 0):
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
