import discord
from discord.ext import commands


class OnlineStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_presence_update(
        self, before: discord.Member, after: discord.Member
    ):
        # Debugging
        # print(f"Before Status: {before.status}")
        # print(f"After Status: {after.status}")

        if (
            before.status == discord.Status.offline
            and after.status == discord.Status.online
        ):
            channel = after.guild.system_channel
            if channel is not None:
                await channel.send(
                    f"""{after.global_name} is now {after.status}"""
                )
            else:
                print("Nowhere to send message")
        else:
            print(f"{after.global_name} is offline")
            return


async def setup(bot):
    await bot.add_cog(OnlineStatus(bot))
