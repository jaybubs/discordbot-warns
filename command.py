import discord
import discord.ext.commands
import req
import collections
import logging
import config

"""
set your log level here
"""
logging.getLogger("req").setLevel(logging.WARN)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.ext.commands.Bot(command_prefix="$", intents=intents)

"""
Warn multifunction to add, subtract, reset or display warns per user
Accepts tagged username, braket uid or untagged username (will try to guesstimate the correct one)
If a user doesn't exist, they will be automatically created
The number of warns a user has will always be printed back by the bot

Usage:
    `$warn stellar` and `$warn stellar +` will equivalently increase the number of warns by 1
    `$warn stellar -` will decrease warns by 1
    `$warn stellar reset` will reset the counter to 0
    `$warn stellar show` (or any other keyword actually) will show the current number of warns
"""

@bot.command()
async def warn(ctx, member: discord.Member, operation="+"):
    data = req.modify_warns(str(member), operation)
    await ctx.send(f"user {data['username']} has {data['warns']} warns")

"""
Display all users that have been warned and how many they got
"""

@bot.command()
async def totals(ctx):
    result = req.list_users()
    sorted_result = collections.OrderedDict(sorted(result.items()))
    # show a neat markdown tabbed struct
    msg = "```md"
    for k,v in sorted_result.items():
        msg += f"\n{k:<20} --> {v}"
    msg += "\n```"
    await ctx.send(msg)

"""
Remove user from the db, so we don't store too many users with 0 warns, or ones that we experiment/joke on
"""
@bot.command()
async def behead(ctx, member: discord.Member):
    data = req.delete_user(str(member))
    await ctx.send(data)

bot.run(config.discord_bot_token)
