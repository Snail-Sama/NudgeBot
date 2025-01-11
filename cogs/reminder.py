import discord
from discord.ext import commands
from discord import app_commands
from discord import utils
import settings
import sqlite3
from .goal import Goal

class Frequency_Select(discord.ui.Select):
    def __init__(self):
        options = [ # Options for reminders
            discord.SelectOption(label="2x Daily", value="2D"),
            discord.SelectOption(label="1x Daily", value="1D"),
            discord.SelectOption(label="Weekly", value="W"),
            discord.SelectOption(label="Monthy", value="M"),
            discord.SelectOption(label="None", value="N"),
        ]
        super().__init__(options=options, placeholder="Would you like a reminder?", min_values=1, max_values=1)

    # Responds to user input
    async def callback(self, interaction:discord.Interaction):
        await self.view.respond_to_answer(interaction, self.values)

class DropdownView(discord.ui.View):
    def __init__(self, *, timeout = 100):
        super().__init__(timeout=timeout)
        self.answer = None
        # Adds the options to the view so the dropdown menu is visible
        self.add_item(Frequency_Select())

    # Logs user input to self.answer and completes the interaction
    async def respond_to_answer(self, interaction:discord.Integration, choices):
        self.answer = choices
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()

class Reminder(commands.Cog):
    @app_commands.command(name="set_reminder", description = "Set your reminder!")
    @app_commands.autocomplete(goal=Goal.goal_choices)
    async def set_reminder(self, interaction: discord.Interaction, goal: int):
        goal_id = goal

        # Sends dropdown menu
        view = DropdownView()
        await interaction.response.send_message(view=view, ephemeral=False) # i want to make this true but it's being annoying

        # Waits for user input
        await view.wait()
        answer = view.answer
        reminder = answer[0]

        # Opens connection to database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        #Finds old reminder
        cursor.execute("SELECT reminder FROM Goals WHERE goal_id = ?", (goal_id,))
        result = cursor.fetchone()
        old_reminder = result[0]

        # Sets new reminder
        cursor.execute("UPDATE Goals SET reminder = ? WHERE goal_id = ?", (reminder, goal_id))
        action = "updated"

        # Close SQL database connection
        connection.commit()
        connection.close()

        await interaction.followup.send(f"Reminder {action} to {reminder} from {old_reminder}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminder(bot))