import discord
from discord.ext import commands
from discord import app_commands, utils
import sqlite3, time, asyncio, schedule, threading, datetime, logging

from nudge_bot.utils.logger import configure_logger
import settings
from nudge_bot.cogs.goalcog import GoalCog
from bot import is_BotMeister

logger = logging.getLogger(__name__)
configure_logger(logger)

class Frequency_Select(discord.ui.Select):
    """List of frequency options for a dropdown menu.
    
    """
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
    async def callback(self, interaction: discord.Interaction):
        """Response to answer?

        """
        logger.info("FrequencySelect callback")
        await self.view.respond_to_answer(interaction, self.values)

class DropdownView(discord.ui.View):
    """Dropdown view for a user to select the frequency of their reminders.
    
    """
    def __init__(self, *, timeout: int = 100):
        super().__init__(timeout=timeout)
        self.answer = None
        # Adds the options to the view so the dropdown menu is visible
        self.add_item(Frequency_Select())


    async def respond_to_answer(self, interaction: discord.Integration, choices: list[str]):
        """Takes user input and disables the dropdown from further interaction.

        Args:
            interaction: The discord interaction with the user.
            choices: List of frequencies the user may choose for their reminder.
        
        """
        logger.info("Responding to answer.")
        self.answer = choices
        self.children[0].disabled = True

        # Resets dropdown and defers interaction until later
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()

class ReminderCog(commands.Cog):
    """Cog for the reminder commands.
    
    """
    def __init__(self, bot: commands.bot) -> None:
        self.bot = bot
        # Creates and runs scheduler for reminders
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()


    def run_scheduler(self) -> None:
        """Run a scheduler in a separate thread and check every minute for a task.
        
        """
        logger.info("Started scheduler.")
        while True:
            logger.info("Scheduler ran all pending.")
            schedule.run_pending()
            time.sleep(60)
    

    async def send_reminder(self, interaction: discord.Interaction, goal_id: int) -> None:
        """Sends reminder mentioning user in the #new-years-resolution channel.

        Args:
            interaction: The discord interaction with the user.
            goal_id: ID of the goal we want to send the reminder for.
        
        """
        logger.info("Sending reminder")
        # Opens connection to database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Gets user, title, and reminder type from goal
        cursor.execute("SELECT user_id, title, reminder FROM Goals WHERE goal_id = ?", (goal_id,))
        user_id, title, reminder = cursor.fetchall()[0]
        user = self.bot.get_user(user_id)

        # Selects string to put in message
        reminder_message = {
            "2D": "twice daily",
            "1D": "once daily",
            "W": "weekly",
            "M": "monthly",
        }.get(reminder)

        # Gets #new-years-resolutions channel
        channel = interaction.guild.get_channel(settings.LOGGER_CH)
        
        await channel.send(f"{user.mention} Don't forget about your goal: {title}! I will remind you {reminder_message} ;)")
    
    # /set_reminder command will set a reminder for a specific goal to send at various intervals
    @app_commands.command(name="set-reminder", description = "Set your reminder!")
    @app_commands.autocomplete(goal_id=GoalCog.goal_autocomplete)
    async def set_reminder(self, interaction: discord.Interaction, goal_id: int) -> None:
        """Set a reminder for a goal to send at various intervals. Sends a followup message upon completion.

        Args:
            interaction: The discord interaction with the user.
            goal_id: ID of the goal we want to set the reminder for.

        Raises:
            TODO implement sql exceptions

        TODO:
            * call a helper funciton
            * ORM
            * Fix action (right now it's only 'updated' not 'set')
        
        """
        logger.info("Received request for setting a reminder.")
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
        cursor.execute("SELECT reminder, job FROM Goals WHERE goal_id = ?", (goal_id,))
        result = cursor.fetchall()
        old_reminder, job = result[0] if result else None

        # Sets new reminder
        cursor.execute("UPDATE Goals SET reminder = ? WHERE goal_id = ?", (reminder, goal_id))
        action = "updated"

        # If a reminder has not already been created, create the job object
        if job == None:
            job = lambda: asyncio.run_coroutine_threadsafe(self.send_reminder(interaction, goal_id), self.bot.loop)

        # Uses schedule library to create a thread for a new reminder
        def schedule_reminder():
            # Checks if the day is the first of the month. If yes, send monthly reminder, else, do nothing
            def send_monthly():
                if datetime.datetime.today().day == 1:
                    job()
                else:
                    None

            # Schedules reminders based on user choice in dropdown
            match reminder:
                case "2D": # Twice Daily
                    schedule.every().day.at("08:00").do(job)
                    schedule.every().day.at("20:00").do(job)
                case "1D": # Once Daily
                    schedule.every().day.at("16:00").do(job)
                case "W": # Once Weekly
                    schedule.every().monday.at("08:00").do(job)
                case "M": # Once Monthly
                    # Shedules the job for every day to send to the send_monthly() method which checks the date before sending reminder
                    schedule.every().day.at("08:00").do(send_monthly)
                case "N": # No reminder
                    if old_reminder != "N" or old_reminder != None:
                        print(schedule.get_jobs())
                        schedule.cancel_job(job)
                        print(schedule.get_jobs())
                case _: # Exception
                    raise Exception("Reminder Invalid")

        
        # Starts thread
        threading.Thread(target=schedule_reminder, daemon=True).start()

        print(schedule.get_jobs())

        cursor.execute("UPDATE Goals SET job = ? WHERE goal_id = ?", (job, goal_id))

        # Close SQL database connection
        connection.commit()
        connection.close()

        logger.info("Reminder created/updated.")
        # Sends response for user
        await interaction.followup.send(f"Reminder {action} to {reminder} from {old_reminder}", ephemeral=True)
    
    # Clears entire reminder schedule (TESTING PURPOSES ONLY)
    @app_commands.command(name="stop-reminder", description = "STOP!")
    @is_BotMeister()
    async def stop_reminder(self, interaction: discord.Interaction) -> None:
        """Clears entire reminder schedule. Must be BotMeister.

        Args:
            interaction: The discord interaction with the user.
        
        """
        logger.info("Received request to stop reminders.")
        schedule.clear()
        await interaction.response.send_message("Stopped", ephemeral=True)


async def setup(bot: commands.bot) -> None:
    await bot.add_cog(ReminderCog(bot))