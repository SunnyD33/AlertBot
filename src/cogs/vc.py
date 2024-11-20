import discord
from discord.ext import commands

from user import User

users = User()


class VoiceChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.User, before, after):
        if after.channel and not member.bot:
            await member.send(
                f"{member.global_name} has joined {after.channel.name} in {after.channel.guild.name}"
            )
        else:
            print(f"{member.global_name} left vc")


async def setup(bot):
    await bot.add_cog(VoiceChat(bot))
