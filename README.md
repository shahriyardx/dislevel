# Dislevel
Making leveling easier for small as well as big bot

# Installation
`pip install dislevel`

# Usage

Making a simple bot with a db connection

```python
from discord.ext import commands
from dislevel import increase_xp

bot = commands.Bot(command_prefix='/')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)
        await increase_xp(message, bot, rate=5)

bot.load_extension('dislevel')

TOKEN = 'TOKEN_HERE'
bot.run(TOKEN)
```

### For subclassed bot

```python
from discord.ext import commands
from dislevel import increase_xp


class MyCustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.user))

    async def on_message(self, message):
        if not message.author.bot:
            self.process_commands(message)
            await increase_xp(message, bot, rate=5)
    

bot = MyCustomBot(command_prefix='/')

bot.load_extension('dislevel')

TOKEN = 'TOKEN_HERE'
bot.run(TOKEN)
```

And setup is done it will automatically configure database and store data in your database

By default it increases exp by 5 whenever `increase_xp` gets called but if you want a different rate then\
`await increase_xp(message, bot, rate=10)`\
Now exp will increase by 10

Run the bot and run the `/rank` command to see your rank

# Commands

**/rank** - `See your rank`
**/leaderboard, /lb** - `See leaderboard`
**/setbg \<url\>** - `Set your bg url`
**/resetbg** - `Reset your bg url to default`
**/levelrole** - `Check level roles`
**/levelrole add \<level\> \<role\>** - `Add a level role`
**/levelrole remove \<level\>** - `Remove a level role`

[Join Discord](https://discord.gg/7SaE8v2) For any kind of help