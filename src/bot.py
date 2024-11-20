import asyncio
import os

import discord
from discord.app_commands.checks import has_permissions
from discord.ext import commands
from dotenv import load_dotenv

import guild_settings
from user import User

load_dotenv()

# Global Veriables
TOKEN = str(os.getenv("BOT_TOKEN"))


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
users = User()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

    print("STATUS MSG: All cogs loaded")


@bot.command(
    name="getid",
    help="Gets your user ID if no user is specified. Otherwise, it will get the ID of the user given",
)
async def getid(ctx, user: discord.User | None):
    requester = ""
    if user is not None:
        requester = user.id
    else:
        requester = ctx.message.author.id

    await ctx.send(users.getUserID(requester))
    # await ctx.send(requester)


@bot.command(
    name="setguildid",
    pass_context=True,
    help="Used to set the guild id for certain commands to work properly. *Requires high level permissions to use*",
)
@has_permissions(manage_roles=True, ban_members=True)
async def setGuildId(ctx, arg1):
    if int(arg1) != int(ctx.message.author.guild.id) or arg1 is None:
        await ctx.send(
            "Double checked to be sure and this doesnt match the guild (server) ID I found. I need to save the proper value for future use"
        )
    elif int(arg1) == ctx.message.author.guild.id:
        guild_settings.setGuildId(guildID=int(arg1))
        await ctx.send("Guild ID stored! Some commands should work better now")


@bot.command(
    name="getguildid",
    pass_context=True,
    help="Used to get the guild id that was set to confirm it matches the current guild id. *Requires high level permissions to use*",
)
@has_permissions(manage_roles=True, ban_members=True)
async def getGuildId(ctx):
    id = guild_settings.getGuildId()
    if id:
        message = (
            f"Guild ID found! Guild ID: {id} *Message deletes in five seconds*"
        )
        msg = await ctx.send(message)
        await asyncio.sleep(5.0)
        await msg.delete()


@bot.command(
    name="members",
    pass_context=True,
    help="Returns a list of members in the guild. *Requires high level permissions to use*",
)
@has_permissions(manage_roles=True, ban_members=True)
async def get_members(ctx):
    guild = ctx.guild
    members = guild.members  # List of all members in the guild
    member_names = [member.display_name for member in members]

    message = f"Members in {guild.name}:\n" + "\n".join(member_names)

    # Send the list of member names to the channel
    msg = await ctx.send(message)
    await asyncio.sleep(5.0)
    await msg.delete()


##############
# ERR Handling
@getGuildId.error
async def getGuildId_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        print("ERR! Guild ID not there")
        await ctx.send(
            "Hmmm, you might not have set the guild ID yet. Try the !setguildid command with your guild id"
        )


@setGuildId.error
async def setGuildId_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        print("ERR! Probably missing the guild ID")
        await ctx.send(
            "I need a guild ID after the command. Right click on the Server name (top left) and select 'Copy Server ID'"
        )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Not a known command. Check your spelling and try again. You can also type !commands to get list of available commands"
        )


#######


async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)


asyncio.run(main())
