# Dislevel
Making leveling easier for small as well as big bot

# Installation
`pip install dislevel`

# Usage

Making a simple bot with a db connection. First of all we need a database connection. Dislevel supports 2 type of database connection, 
- `asyncpg (Pool)`
- `databases (Database)`

If your bot already have a connection you can use that, Or you can create a new one for leveling. In this example I will create a new connection using databases[sqlite]


```py
from databases import Database
from discord import Intents
from discord.ext import commands

from dislevel import init_dislevel
from dislevel.utils import update_xp

intents = Intents.default()
# Nextcord current version uses discord Api v9 where message content intent is not enforced. 
# If you ware are using discord.py when you will need to enable message_content intent manually as shown below
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    # Using databases to create a sqlite db
    db = Database("sqlite:///leveling.db")
    await db.connect()

    # Pass instance of bot, the database connection and specify which driver to use. In this case we are using databases so we passed that
    await init_dislevel(bot, db, "databases") 

    # Load the cog. It has two cogs. `dislevel.nextcord`, `dislevel.dpy`
    bot.load_extension("dislevel.dpy")

    print("Ready! Let's go...")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # You can use this method anywhere to update xp of a member
    # First pass the bot instance, member_id, guild_id and how much xp to be added.
    await update_xp(bot, message.author.id, message.guild.id, amount=10)

    await bot.process_commands(message)

TOKEN: str = "Your bot token here"
bot.run(TOKEN)
```

# Events
```py
# If you want to do something when a user level's up!
@bot.event
async def on_dislevel_levelup(guild_id, member_id, level):
    print(f"Member level up! ID: {member_id}")
````

# Commands

**rank [member]** - `See your/member's rank` \
**leaderboard, lb** - `See leaderboard` \
**setbg \<url\>** - `Set your bg url` \
**resetbg** - `Reset your bg url to default` \

[Join Discord](https://discord.gg/7SaE8v2) For any kind of help