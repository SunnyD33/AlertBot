import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import guild_settings
from user import User

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

# Global Veriables
TOKEN = str(os.getenv("BOT_TOKEN"))


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
users = User()


####
# Bot initialization
####
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

    logging.info("STATUS MSG: All cogs loaded")


# Pre-processing controls
@bot.event
async def on_message(message):
    if message.content.startswith("!"):
        logging.info(
            f"Command '{message.content}' received from user {message.author.global_name}; Checking opt in/out status"
        )

        opt_status = guild_settings.is_opted_in(message.author.id)
        if not opt_status and not isinstance(
            message.channel, discord.DMChannel
        ):
            ctx = await bot.get_context(message)
            await ctx.send(
                "You're not opted in to use me, so commands will not work. To opt in, DM me using the !optin command."
            )
            return
        else:
            await bot.process_commands(message)

    # To allow alert bot to alert users when someone mentions them in a discord channel
    if message.mentions:
        for mentioned_user in message.mentions:
            logging.info(f"{message.author.global_name} mentioned someone")
            try:
                # Send a DM to the mentioned user
                if (
                    mentioned_user != message.author
                ):  # Avoid notifying the sender
                    message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                    await mentioned_user.send(
                        f"{message.author.display_name} mentioned you in {message.channel} from the {message.guild} server:\n\n"
                        f"**Message:** {message.content}\n"
                        f"Click here to jump to the message {message_link}"
                    )
            except discord.Forbidden:
                # The bot couldn't DM the user
                logging.info(
                    f"Could not send DM to {mentioned_user.display_name}"
                )


# Commands
@bot.command(
    name="getid",
    help="Gets your user ID if no user is specified. Otherwise, it will get the ID of the user given (need admin rights)",
)
async def getid(ctx, user: discord.User | None):
    if ctx.guild is None:
        requester = ""
        if user is not None:
            requester = user.id
        else:
            requester = ctx.message.author.id

        msg = await ctx.send(
            f"{users.getUserID(requester)}\n Message will delete in 5 seconds, so be quick"
        )
        await asyncio.sleep(5.0)
        await msg.delete()
        logging.info("message deleted successfully")
    else:
        await ctx.send(
            "Not a good idea to run this command here. DM me this command for this!"
        )


@bot.command(
    name="setguildid",
    pass_context=True,
    help="Used to set the guild id for certain commands to work properly. *Requires high level permissions to use*",
)
@commands.has_permissions(administrator=True)
async def setGuildId(ctx, arg1):
    intial_id = arg1
    if not guild_settings.is_opted_in(ctx.author.id):
        await ctx.send(
            "You're not opted in to do run this command! Also...make sure you have the proper permissions to run this even if you are opted in!"
        )
        return
    if guild_settings.is_opted_in(ctx.author.id):
        await ctx.send(
            "Please enter the guild ID again to confirm (you have 30 seconds to lock it in). Enter Cancel or cancel to not store a guild ID. If you need help finding the guild ID, cancel this and run !findguildid in the guild where I am invited."
        )
        await ctx.send(
            "Enter None or none to remove the guild ID that is set. Note, this will make me less functional..."
        )

        def check(mes):
            return mes.author == ctx.author

        try:
            # Wait for a message from the user with a 30-second timeout
            msg = await bot.wait_for("message", timeout=30.0, check=check)
            if intial_id == msg.content:
                guild_settings.setGuildId(guildID=int(msg.content))
                await ctx.send("Guild ID stored!")
                return
            if msg.content == "Cancel" or msg.content == "cancel":
                await ctx.send("Operation cancelled. Guild ID not stored")
                return
            if msg.content == "None" or msg.content == "none":
                guild_settings.removeGuildID(guildID=int(msg.content))
                await ctx.send(
                    "Guild ID removed. Hope you know what you were doing.."
                )
                return
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Guild ID not saved")
            return
    else:
        await ctx.send(
            "You dont have proper permissions to run this. You need admin permissions to use this"
        )


@bot.command(
    name="getguildid",
    pass_context=True,
    help="Used to get the guild id that was set to confirm it matches the current guild id. *Requires high level permissions to use*",
)
@commands.has_permissions(administrator=True)
async def getGuildId(ctx):
    if not guild_settings.is_opted_in(ctx.author.id):
        await ctx.send(
            "You're not opted in to do run this command! Also...make sure you have the proper permissions to run this even if you are opted in!"
        )
        return

    id = guild_settings.getGuildId()
    if id:
        message = (
            f"Guild ID found! Guild ID: {id} *Message deletes in five seconds*"
        )
        msg = await ctx.send(message)
        await asyncio.sleep(5.0)
        await msg.delete()


@bot.command(
    name="findguildid",
    pass_context=True,
    help="Tells users how to find the guild ID where they want to use me",
)
@commands.has_permissions(administrator=True)
async def findguildid(ctx):
    await ctx.send(
        "Go to the guild where I am currently invited to go to the top right where the guild name is and right click it. Select 'Copy Server ID' and it will be on your clipboard."
    )
    await ctx.send(
        "Use this ID for the !setguildcommand (if you have the proper permissions to run the command)"
    )


@bot.command(
    name="members",
    pass_context=True,
    help="Returns a list of members in the guild. *Requires high level permissions to use*",
)
@commands.has_permissions(manage_roles=True, ban_members=True)
async def get_members(ctx):
    guild = ctx.guild
    members = guild.members  # List of all members in the guild
    member_names = [member.display_name for member in members]

    message = f"Members in {guild.name}:\n" + "\n".join(member_names)

    # Send the list of member names to the channel
    msg = await ctx.send(message)
    await ctx.send("Will delete in ten seconds..")
    await asyncio.sleep(10.0)
    await msg.delete()


@bot.command(
    name="optin",
    pass_context=True,
    help="Used to opt-in to use Alert Bot",
)
async def opt_in(ctx):
    if ctx.guild is None:
        # Run a check to see if user is already opted in and halt this command
        opt_check = guild_settings.is_opted_in(ctx.author.id)

        if opt_check:
            await ctx.send(
                "You're already opted in. Cancelling command. You can use the !optstatus command in the future to check current status."
            )
            return

        await ctx.send("Opting in...")
        guild_settings.opt_in(ctx.author.id)
        opt_status = guild_settings.is_opted_in

        if opt_status:
            await ctx.send(
                "You're all set. You can now use commands in the disord where I am invited to!"
            )
        else:
            await ctx.send(
                "Odd..something went wrong. Report this to my creator(s) to look into"
            )  # Should not happen
    else:
        await ctx.send(
            "You can't run this command here. This works in DM only.\nPlus if you see this message, you're already opted in."
        )


@bot.command(
    name="optout",
    pass_context=True,
    help="Used to opt-out of using Alert Bot",
)
async def opt_out(ctx):
    if ctx.guild is None:
        await ctx.send("Opting out...")
        guild_settings.opt_out(ctx.author.id)
        opt_status = guild_settings.is_opted_in

        if opt_status:
            await ctx.send(
                "All set. You have opted out. You will no longer get notified personally from me.\n You can always opt back in later"
            )
        else:
            await ctx.send(
                "Oof...this shouldn't happen Report this to my creator(s) to look into"
            )  # I mean...it says it

    else:
        await ctx.send(
            "You can't run this command here. This works in DM only."
        )


@bot.command(
    name="optstatus",
    pass_context=True,
    help="Returns the opt status back to the user",
)
async def get_opt_stat(ctx):
    if ctx.guild is None:
        opt_status = guild_settings.is_opted_in(ctx.author.id)
        if opt_status:
            await ctx.send(
                "You are currently opted in. You can opt out or mute notifications"
            )
        else:
            await ctx.send(
                "You are currently not opted in. You can opt in by running the !optin command"
            )
    else:
        await ctx.send("DM me for this so we don't bother everyone with it")


@bot.command(
    name="checkperms",
    pass_context=True,
    help="Used to check current permissions of the user who ran the command",
)
async def check_permissions(ctx):
    perms = ctx.author.guild_permissions

    if perms.administrator:
        await ctx.send(
            "You have admin rights! You can run any command. Wield this power properly.."
        )
    elif perms.manage_roles or perms.ban_members:
        await ctx.send(
            "You have the ability to at least ban members and/or manage roles. You have some flex but not all"
        )
    else:
        await ctx.send(
            "You dont have any special permissions. Commands are limited."
        )


##############
# ERR Handling
##############
@getGuildId.error
async def getGuildId_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        print("ERR! Guild ID not there")
        await ctx.send(
            "Hmmm, you might not have set the guild ID yet. Try the !setguildid command with your guild id"
        )
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Looks like you don't have the proper permissions to run this command"
        )


@setGuildId.error
async def setGuildId_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        print("ERR! Probably missing the guild ID")
        await ctx.send(
            "I need a guild ID after the command. Run !findguildid in the server where I am invited to get the guild ID'"
        )
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Looks like you don't have the proper permissions to run this command"
        )


@get_members.error
async def members_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Looks like you don't have the proper permissions to run this command"
        )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        if ctx.guild:
            await ctx.send(
                "Not a known command. Check your spelling and try again. You can also type !help to get list of available commands"
            )
        else:
            await ctx.send(
                "Hmm, not something I can help with here. You can opt in, opt out, check opt status or mute yourself here.\nTo use other commands, use the Discord where I am invited"
            )


#######


async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)


asyncio.run(main())
