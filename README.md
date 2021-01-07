# Dislevel
Making leveling easier for small as well as big bot

# Installation
`pip install dislevel`

# Usage

Making a simple bot with a db connection

```python
import os
from discord.ext import commands
import aiosqlite


bot = commands.Bot(command_prefix='/')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    await bot.process_commands(message)


async def connect_db():
    connection = await aiosqlite.connect("leveling.db")
    
    # for postgresql
    # import asyncpg # Import in the begining of the file
    # db = await asyncpg.connect(user='username', password='password', database='database_name', host='localhost')
    
    bot.db = connection

# Setup db for leveling
# As we assinged the database connection variabled named `db` that will be used for database
# Now set environment variable named `DISLEVEL_DB_CONN` and set value to the name of the variable assigned to the bot which is `db`
# Note : Connection must be made using aiosqlite for SQLite databse and asyncpg for PostgreSQL
os.environ['DISLEVEL_DB_CONN'] = 'db'

TOKEN = 'TOKEN_HERE'

bot.loop.run_until_complete(connect_db())

# Loading the cog/extension so we can use the functionality
bot.load_extension('dislevel')

bot.run(TOKEN)
```

### For subclassed bot

```python
from discord.ext import commands
import aiosqlite
import os


class MyCustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.user))

    async def on_message(self, message):
        self.process_commands(message)
    

bot = MyCustomBot(command_prefix='/')
async def connect_db():
    connection = await aiosqlite.connect("leveling.db")
    
    # for postgresql
    # import asyncpg # Import in the begining of the file
    # db = await asyncpg.connect(user='username', password='password', database='database_name', host='localhost')
    
    bot.db = connection
# Setup db for leveling
# As we assinged the database connection variabled named `db` that will be used for database
# Now set environment variable named `DISLEVEL_DB_CONN` and set value to the name of the variable assigned to the bot which is `db`
# Note : Connection must be made using aiosqlite for SQLite databse and asyncpg for PostgreSQL
os.environ['DISLEVEL_DB_CONN'] = 'db'

TOKEN = 'TOKEN_HERE'

bot.loop.run_until_complete(connect_db())

# Loading the cog/extension so we can use the functionality
bot.load_extension('dislevel')

bot.run(TOKEN)
```

And setup is done it will automatically configure database and store data in your database

For increasing exp on every message

`from dislevel import increase_xp`

and then whenever you want to increase exp which maybe in `on_message`
Put: `await increase_xp(message, bot)`
Here `message` is a `discord.Message` object and `bot` is the actual bot object

By default it increases exp by 5 whenever `increase_xp` gets called but if you want a different rate then
`await increase_xp(message, bot, rate=10)`
Now exp will increase by 10

Here amount must be an string of an integer.
Run the bot and run the `/rank` command to see your rank