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
            exp INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 1
        )
    """
    )

    bot.level_db_prepared = True


async def update_data(member, row_id, exp, level, new_level, bot):
    """Update specific row with given data"""
    if new_level > level:
        level = new_level
        bot.dispatch('level_up', member, level, exp)

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


async def get_user_data(member, bot):
    await prepare_db(bot)

    data = await get_data(member.id, member.guild.id, bot)
    user_data = {
        "user_id": data[1],
        "guild_id": data[2],
        "current_user_exp": data[3],
        "current_level_min_xp": data[4] ** 5,
        "xp_required_for_next_level": (data[4] + 1) ** 5,
        "xp_required": ((data[4] + 1) ** 5) - data[3],
        "level": data[4],
        "position": data[5],
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
