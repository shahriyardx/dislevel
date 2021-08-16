from numerize.numerize import numerize


async def prepare_db(bot):
    """Prepare database for leveling"""
    if bot.level_db_prepared:
        return

    await bot.level_db.execute(
        """
        CREATE TABLE IF NOT EXISTS leveling(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            exp INTEGER NOT NULL DEFAULT 1,
            level INTEGER NOT NULL DEFAULT 1,
            rep INTEGER NOT NULL DEFAULT 1,
            bg_image TEXT NULL
        )
    """
    )

    await bot.level_db.execute(
        """
        CREATE TABLE IF NOT EXISTS leveling_roles(
            id INTEGER PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            level INTEGER NOT NULL
        )
    """
    )

    bot.level_db_prepared = True


async def update_data(member, row_id, exp, level, new_level, bot):
    """Update specific row with given data"""
    if new_level > level:
        level = new_level

        level_role = await bot.level_db.fetch_one(
            "SELECT * FROM leveling_roles WHERE guild_id=:guild_id AND level=:level",
            {"guild_id": member.guild.id, "level": level},
        )

        if level_role:
            role = member.guild.get_role(level_role[2])
            if role:
                await member.add_roles(role)

        bot.dispatch("level_up", member, level, exp)

    await bot.level_db.execute(
        "UPDATE leveling SET exp=:exp, level=:level WHERE id=:id",
        {"exp": exp, "level": level, "id": row_id},
    )


async def get_data(user_id, guild_id, bot):
    """Get exp data"""

    user_data = await bot.level_db.fetch_one(
        "SELECT * FROM leveling WHERE user_id=:user_id and guild_id=:guild_id",
        {"user_id": user_id, "guild_id": guild_id},
    )

    if not user_data:
        await bot.level_db.execute(
            "INSERT INTO leveling(user_id, guild_id) VALUES(:user_id, :guild_id)",
            {"user_id": user_id, "guild_id": guild_id},
        )

        user_data = await bot.level_db.fetch_one(
            "SELECT * FROM leveling WHERE user_id=:user_id and guild_id=:guild_id",
            {"user_id": user_id, "guild_id": guild_id},
        )

    guild_data = await bot.level_db.fetch_all(
        "SELECT * FROM leveling WHERE guild_id=:guild_id ORDER BY exp DESC",
        {"guild_id": guild_id},
    )

    position = 0
    for row in guild_data:
        position += 1
        if row[1] == user_data[1]:
            break

    user_data = [x for x in user_data]
    user_data.append(position)
    return user_data


async def increase_xp(message, bot, rate=5):
    await prepare_db(bot)

    user_data = await get_data(message.author.id, message.guild.id, bot)
    if user_data:
        exp = user_data[3] + rate
        level = user_data[4]
        new_level = int(exp ** (1 / 5))

        await update_data(message.author, user_data[0], exp, level, new_level, bot)


async def get_next_role(bot, guild, level):
    roles = await bot.level_db.fetch_all(
        "SELECT * FROM leveling_roles WHERE guild_id=:guild_id AND level > :level",
        {"guild_id": guild.id, "level": level},
    )

    role_name = None

    for role in roles:
        guild = bot.get_guild(role[1])
        if not guild:
            continue

        role = guild.get_role(role[2])
        if not role:
            continue

        role_name = str(role)
        break

    return role_name


async def give_rep(bot, member):
    await prepare_db(bot)

    user_data = await get_data(member.id, member.guild.id, bot)
    rep = user_data[5]

    await bot.level_db.execute(
        "UPDATE leveling SET rep=:rep WHERE id=:id",
        {"rep": rep + 1, "id": user_data[0]},
    )


async def get_user_data(member, bot):
    await prepare_db(bot)

    data = await get_data(member.id, member.guild.id, bot)

    user_xp = data[3]
    user_level = data[4]
    min_xp = user_level ** 5
    next_level_exp = (user_level + 1) ** 5
    xp_required = next_level_exp - min_xp
    xp_have = user_xp - min_xp
    percentage = (100 * xp_have) / xp_required

    next_role = await get_next_role(bot, member.guild, user_level)

    user_data = {
        "current_user_exp": numerize(user_xp),
        "next_level_exp": numerize((user_level + 1) ** 5),
        "percentage": percentage,
        "level": str(user_level),
        "rep": str(data[5]),
        "bg_image": str(data[6]),
        "position": str(data[7]),
        "next_role": next_role,
    }

    return user_data


async def get_leaderboard_data(bot, guild_id=None, is_global=False):
    await prepare_db(bot)

    if not is_global:
        data = await bot.level_db.fetch_all(
            "SELECT * FROM leveling WHERE guild_id=:guild_id ORDER BY exp DESC LIMIT 10",
            {"guild_id": guild_id},
        )
    else:
        data = await bot.level_db.fetch_all(
            "SELECT * FROM leveling ORDER BY exp DESC LIMIT 10"
        )

    return data


async def add_level_role(bot, guild_id, level, role_id):
    """Assign a role to a level"""

    await prepare_db(bot)

    guild_role = await bot.level_db.fetch_one(
        "SELECT * FROM leveling_roles WHERE guild_id=:guild_id AND role_id=:role_id",
        {"guild_id": guild_id, "role_id": role_id},
    )
    if guild_role:
        return f"This role has already been assigned to level `{guild_role[3]}`."

    level_role = await bot.level_db.fetch_one(
        "SELECT * FROM leveling_roles WHERE guild_id=:guild_id AND level=:level",
        {"guild_id": guild_id, "level": level},
    )

    if level_role:
        return f"This level already has a role assigned."

    await bot.level_db.execute(
        "INSERT INTO leveling_roles(guild_id, role_id, level) VALUES(:guild_id, :role_id, :level)",
        {"guild_id": guild_id, "role_id": role_id, "level": level},
    )

    return "Level role added."


async def remove_level_role(bot, guild_id, level):
    """Remove a level role"""
    level_role = await bot.level_db.fetch_one(
        "SELECT * FROM leveling_roles WHERE guild_id=:guild_id AND level=:level",
        {"guild_id": guild_id, "level": level},
    )

    if not level_role:
        return f"No level role found on level `{level}`."

    await bot.level_db.execute(
        "DELETE FROM leveling_roles WHERE guild_id=:guild_id AND level=:level",
        {"guild_id": guild_id, "level": level},
    )

    return "Level role removed."


async def get_level_roles(bot, guild):
    roles = await bot.level_db.fetch_all(
        "SELECT * FROM leveling_roles WHERE guild_id=:guild_id ORDER BY level",
        {"guild_id": guild.id},
    )

    the_roles = {}
    for role in roles:
        the_role = guild.get_role(role[2])
        if the_role:
            the_roles[role[3]] = the_role

    return the_roles
