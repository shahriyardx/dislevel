import os
from typing import List, Union

from ._models import Field

leveling_table: str = None


async def prepare_db(database, additional_fields: List[Field] = list()) -> None:
    """Prepares the database for leveling"""
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    default_fields = [
        Field(name="id", type="BIGSERIAL", primary=True),
        Field(name="member_id", type="BIGINT", null=False),
        Field(name="guild_id", type="BIGINT", null=False),
        Field(name="xp", type="BIGINT", null=False, default=0),
        Field(name="level", type="BIGINT", null=False, default=1),
        Field(name="bg_image", type="TEXT"),
        Field(name="text_color", type="TEXT"),
        Field(name="text_color2", type="TEXT"),
        Field(name="text_color3", type="TEXT"), 
    ]

    all_fields = default_fields + additional_fields
    field_schema = ""

    for index, field in enumerate(all_fields):
        statement = f"{field.name} {field.type}"

        if field.primary:
            statement += " PRIMARY KEY"

        if not field.null:
            statement += " NOT NULL"

        if field.default != None:
            statement = f"{statement} DEFAULT %r" % field.default

        field_schema += statement + (", " if index < len(all_fields) - 1 else "")

    schema = f"CREATE TABLE IF NOT EXISTS {leveling_table}({field_schema})"

    try:
        await database.execute(schema)
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
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    data = await database.fetch_one(
        f"""
        SELECT  * 
        FROM    {leveling_table} 
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
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    data = await database.fetch_all(
        f"""
        SELECT   member_id, xp
        FROM     {leveling_table}
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
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    data = await database.fetch_all(
        f"""SELECT  *
             FROM   {leveling_table} 
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
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    user_data = await get_member_data(bot, member_id, guild_id)

    if user_data:
        level = user_data["level"]
        new_xp = user_data["xp"] + amount
        new_level = int(new_xp ** (1 / 5))

        await database.execute(
            f"""
            UPDATE  {leveling_table} 
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
            INSERT  INTO {leveling_table}
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
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    await database.executec(
        f"""
        DELETE  FROM {leveling_table}
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
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    await database.execute(
        f"""
        UPDATE  {leveling_table}
        SET     bg_image = :bg_image
        WHERE   guild_id = :guild_id
        AND     member_id = :member_id 
        """,
        {"bg_image": url, "guild_id": guild_id, "member_id": member_id},
    )

async def set_text_color(bot, member_id: int, guild_id: str, color, color2, color3) -> None:
    """Set text color"""
    database = bot.dislevel_database
    leveling_table = os.environ.get("DISLEVEL_TABLE")

    await database.execute(
        f"""
        UPDATE  {leveling_table}
        SET     text_color = :text_color
        WHERE   guild_id = :guild_id
        AND     member_id = :member_id 
        """,
        {"text_color": color, "guild_id": guild_id, "member_id": member_id},
    )
    await database.execute(
        f"""
        UPDATE  {leveling_table}
        SET     text_color2 = :text_color2
        WHERE   guild_id = :guild_id
        AND     member_id = :member_id 
        """,
        {"text_color2": color2, "guild_id": guild_id, "member_id": member_id},
    )
    await database.execute(
        f"""
        UPDATE  {leveling_table}
        SET     text_color3 = :text_color3
        WHERE   guild_id = :guild_id
        AND     member_id = :member_id 
        """,
        {"text_color3": color3, "guild_id": guild_id, "member_id": member_id},
    )
