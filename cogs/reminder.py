import discord
from discord.ext import commands
from discord import app_commands
from discord import utils
import settings
import sqlite3
from .goal import Goal
import time, asyncio, schedule, threading
from datetime import timedelta
from bot import is_BotMeister

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
    def __init__(self, *, timeout: int = 100):
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
    def __init__(self, bot):
        self.bot = bot
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def run_scheduler(self):
        # Runs the schedule in a separate thread
        while True:
            print(schedule.get_jobs())
            schedule.run_pending()
            time.sleep(60)  # Check every second for scheduled task
    
    # @app_commands.command(name="send_reminder", description = "Send your reminder!")
    # @app_commands.autocomplete(goal_id=Goal.goal_choices)
    async def send_reminder(self, interaction: discord.Interaction, goal_id: int):
        # Opens connection to database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()
        # Gets user, title, and reminder type from goal
        cursor.execute("SELECT user_id, title, reminder FROM Goals WHERE goal_id = ?", (goal_id,))
        user_id, title, reminder = cursor.fetchall()[0]

        user = self.bot.get_user(user_id)

        reminder_message = {
            "2D": "twice daily",
            "1D": "once daily",
            "W": "weekly",
            "M": "monthly",
        }.get(reminder)

        await interaction.followup.send(f"{user.mention} Don't forget about your goal: {title}! I will remind you {reminder_message} ;)")

    # async def schedule_reminder(self, interaction: discord.Interaction, goal_id: int):
    #     schedule.every(1).day.do(send_reminder, interaction, goal_id)

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
        old_reminder = result[0] if result else None

        # Sets new reminder
        cursor.execute("UPDATE Goals SET reminder = ? WHERE goal_id = ?", (reminder, goal_id))
        action = "updated"

        # Close SQL database connection
        connection.commit()
        connection.close()

        delay = {
            "2D": schedule,
            "1D": 1 * 24 * 3600,
            "W": 7 * 24 * 3600,
            "M": 30 * 24 * 3600,  # Approximation of a month
        }.get(reminder)

        if delay is None:
            await interaction.followup.send("Invalid reminder", ephemeral=True)
            return

        def schedule_reminder():
            schedule.every(delay).seconds.do(
                            lambda: asyncio.run_coroutine_threadsafe(
                            self.send_reminder(interaction, goal_id), self.bot.loop
                        )
            )

        threading.Thread(target=schedule_reminder, daemon=True).start()

        await interaction.followup.send(f"Reminder {action} to {reminder} from {old_reminder}", ephemeral=True)

    @app_commands.command(name="stop_reminder", description = "STOP!")
    @is_BotMeister()
    async def stop_reminder(self, interaction: discord.Interaction):
        schedule.clear()
        await interaction.response.send_message("Stopped", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminder(bot))