import asyncio

import discord
from discord.ext import commands
from discord.ui import Button, View

# Store presence counts
user_presence_status = {}

checkmark = "\u2705"  # ✅
crossmark = "\u274c"  # ❌


class Summon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Used to ping the server to get people's attention. You can list multiple names as long as they are in the guild. Only requires a space between each name. *Good for raid attendance*"
    )
    async def summon(self, ctx, *usernames: str):
        """
        usernames: List of usernames to track presence in the guild
        """

        timeout: float = 300.0  # Set the timeout to 5 minutes (300 seconds)
        cancel_event = asyncio.Event()

        if not usernames:
            await ctx.send("Please provide usernames to track presence.")
            return

        # Validate usernames
        guild_members = {
            member.display_name: member for member in ctx.guild.members
        }
        invalid_usernames = []
        valid_users = []

        for username in usernames:
            if username in guild_members:
                valid_users.append(guild_members[username])
                user_presence_status[guild_members[username].id] = False
            else:
                invalid_usernames.append(username)

        # Notify the user about invalid usernames
        if invalid_usernames:
            await ctx.send(
                f"The following usernames are not members of the guild: {', '.join(invalid_usernames)}"
            )

        # If no valid users are provided, exit the command
        if not valid_users:
            await ctx.send("No valid users were provided to track presence.")
            return

        # Create an embed to show the presence status
        embed = discord.Embed(
            title="Attendance List", color=discord.Color.green()
        )
        embed.description = "Click the button to mark yourself as present!"

        # Add users and initial status
        for user in valid_users:
            embed.add_field(
                name=user.display_name,
                value="Present: " + crossmark,
                inline=False,
            )

        # Add the timer field to the embed
        embed.add_field(
            name="Time Remaining", value="300 seconds", inline=False
        )

        # Button for tracking presence
        button_present = Button(
            label="Mark Present", style=discord.ButtonStyle.primary
        )

        async def present_button_callback(interaction):
            if interaction.user.id in user_presence_status:
                # Check if the user has already marked themselves present
                if user_presence_status[interaction.user.id]:
                    # Send an ephemeral message if already checked in
                    await interaction.response.send_message(
                        "You have already checked in!", ephemeral=True
                    )
                else:
                    # Update the user's presence status to present
                    user_presence_status[interaction.user.id] = True

                    # Update the embed to reflect the new presence status
                    for index, user in enumerate(valid_users):
                        status = (
                            "✅" if user_presence_status[user.id] else crossmark
                        )
                        embed.set_field_at(
                            index,
                            name=user.display_name,
                            value=f"Present: {status}",
                            inline=False,
                        )

                    # Edit the message to show the updated embed
                    await interaction.response.edit_message(embed=embed)

                    # Check if all users have checked in
                    if all(
                        user_presence_status[user.id] for user in valid_users
                    ):
                        # Stop the timer and set the time remaining to "Complete"
                        embed.set_field_at(
                            -1,
                            name="Time Remaining",
                            value="Complete",
                            inline=False,
                        )
                        # Disable the buttons
                        button_present.disabled = True
                        button_cancel.disabled = True
                        await interaction.edit_original_response(
                            embed=embed, view=view
                        )

                        cancel_event.set()

                        return

            else:
                # Notify if the user wasn't part of the original list
                await interaction.response.send_message(
                    "You were not listed in the command.", ephemeral=True
                )

        # Button for canceling the action
        button_cancel = Button(label="Cancel", style=discord.ButtonStyle.danger)

        async def cancel_button_callback(interaction):
            cancel_event.set()

            # Notify the user that they canceled the action
            await interaction.response.send_message(
                f"{interaction.user.display_name} has canceled the summons."
            )

            # Mark all users as not present
            for index, user in enumerate(valid_users):
                embed.set_field_at(
                    index,
                    name=user.display_name,
                    value=f"Present: {crossmark}",
                    inline=False,
                )

            # Set the timer field to canceled
            embed.set_field_at(
                -1,
                name="Time Remaining",
                value="Canceled",
                inline=False,
            )

            # Disable the buttons
            button_present.disabled = True
            button_cancel.disabled = True
            await interaction.edit_original_response(view=view, embed=embed)

        # Attach the callback to the button
        button_present.callback = present_button_callback
        button_cancel.callback = cancel_button_callback

        # Add the button to the view and send the embed
        view = View(timeout=timeout)
        view.add_item(button_present)
        view.add_item(button_cancel)
        message = await ctx.send(embed=embed, view=view)

        # Timer countdown function
        async def update_timer():
            countdown = 300  # Timer set for 300 seconds (5 minutes)
            while countdown > 0:
                if (
                    cancel_event.is_set()
                ):  # Check if the cancel button was pressed
                    break  # Stop the timer if cancel was clicked

                embed.set_field_at(
                    -1,
                    name="Time Remaining",
                    value=f"{countdown} seconds",
                    inline=False,
                )
                await message.edit(embed=embed)
                await asyncio.sleep(1)  # Update every second
                countdown -= 1

            # Time's up or canceled, disable the buttons and update embed
            button_present.disabled = True
            button_cancel.disabled = True
            embed.set_field_at(
                -1,
                name="Time Remaining",
                value="Time's up!"
                if countdown == 0
                else "Complete (All checked in)",
                inline=False,
            )
            await message.edit(embed=embed, view=view)

        # Start the timer countdown
        await update_timer()


async def setup(bot):
    await bot.add_cog(Summon(bot))
