import discord
from discord.ext import commands
from discord import app_commands
import settings, logging, sqlite3, typing

from sqlalchemy import Text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from nudge_bot.db import db
from nudge_bot.utils.logger import configure_logger
from nudge_bot.models.goal import Goal

logger = logging.getLogger(__name__)
configure_logger(logger)

class GoalModal(discord.ui.Modal, title="Enter your goal here!"):
    """Modal for the user to submit their goal.
    
    Attributes:
        goal_title: Short text input for title of goal (required).
        goal_description: Long text input for description of goal (not required).
        goal_target: Short text input for target of goal; should be an int (required).
        goal_id: Goal ID which user does not input but used for edit_goal; should be an int.

    """
    goal_title = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Title",
        required = True,
        placeholder = "A short title of your goal!"
    )
    goal_description = discord.ui.TextInput(
        style = discord.TextStyle.long,
        label = "Description",
        required = False,
        max_length = 500,
        placeholder = "Describe the goal you want to achieve!"
    )
    goal_target = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Target",
        required = True,
        placeholder = "Enter the number in your goal! Ex: the '100' in 100 push-ups"
    )

    goal_id = None

    async def on_submit(self, interaction : discord.Interaction) -> str:
        """Asynchronous method for when users submit their goal information in the modal. 
        Sends an embed with basic information about the goal in the interaction channel and a confirmation message upon completion.

        Args:
            interaction: The discord interaction of the user's request.

        """
        logger.info(f"User submitted modal.")
        action = Goal.create_goal(interaction.user.id, self.goal_title.value, self.goal_description.value, self.goal_target.value, "N")
        channel = interaction.guild.get_channel(settings.LOGGER_CH)

        embed = discord.Embed(title=self.goal_title.value,
                              description=self.goal_description.value,
                              color=discord.Color.yellow())
        embed.set_author(name=interaction.user.name)

        logger.info("Sending embed and response.")
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Succesfully {action} goal!", ephemeral=True)

    async def on_error(self, interaction : discord.Interaction, error):
        ...


class GoalCog(commands.Cog): # Goal(commands.Cog, db.Model):
    """Class for describing the Cog relating to any goal commands.
    
    """
    async def goal_autocomplete(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[int]]:
        """Fetches all goal IDs linked with user ID for autocopmlete.

        Args:
            interaction: The discord interaction.
            current: The string of characters the user has currently typed out.

        Returns:
            choices: The list of choices the user has that are autocompleted from the current string.

        TODO: 
            implement ORM here

        """
        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Fetch goal_ids under a user
        cursor.execute("SELECT goal_id, title FROM Goals WHERE user_id = ?", (interaction.user.id,))
        goal_ids = cursor.fetchall()

        # Close SQL database connection
        connection.close()

        # Create autocomplete choices
        choices = []
        for goal_id, title in goal_ids:
            if current.lower() in title.lower():
                choices.append(app_commands.Choice(name=title, value=goal_id))

        return choices
    

    @app_commands.command(name="create-goal", description="Set a new goal!")
    async def create_goal_command(self, interaction : discord.Interaction):
        """User creates a goal using command .create-goal and sends a GoalModal instance for them to input their goal data.

        Args:
            interaction: The discord interaction of the user's request.
    
        """
        logger.info(f"Received request to create a goal. Sending modal...")
        goal_modal = GoalModal()
        await interaction.response.send_modal(goal_modal)


    @app_commands.command(name="delete-goal", description="Delete one of your goals")
    @app_commands.autocomplete(goal_id=goal_autocomplete)
    async def delete_goal(self, interaction: discord.Interaction, goal_id: int):
        """User deletes a goal using command .delete-goal and sends confirmation upon completion

        Args: 
            interaction: The discord interaction of the user's request.

        Raises:
            TODO implement error where if there does not exist a goal following their request
        
        TODO:
            add logging
            call a Goals function instead for high cohesion (use ORM)

        """
        logger.info(f"Received request to delete a goal.")
        Goal.delete_goal(goal_id)

        await interaction.response.send_message(f"Successfully deleted goal", ephemeral=True)


    @app_commands.command(name="log", description="log progress towards a goal")
    @app_commands.autocomplete(goal_id=goal_autocomplete)
    async def log_goal(self, interaction: discord.Interaction, goal_id: int, entry: int):
        """User logs progress towards one of their goals and sends confirmation upon completion.
        
        Args:
            interaction: The discord interaction of the user's request.
            goal_id: The goal ID that the user wishes to log progress towards.
            entry: The amount of progress the user made towards their goal.

        Raises:
            TODO implement error when the goal does not exist
            TODO implement error for any other sql error

        """
        logger.info(f"Received request to log progress to a goal...")

        (completed, title, description) = Goal.log_goal(goal_id, entry)

        #create and send completion embed
        if completed:
            channel = interaction.guild.get_channel(settings.LOGGER_CH)
            embed = discord.Embed(title=f"Completed {title}",
                                description=description,
                                color=discord.Color.brand_green())
            embed.set_author(name=interaction.user.name)
            await channel.send(embed=embed)
        
        
        await interaction.response.send_message(f"Successfully logged {entry} to your progress", ephemeral=True)


    @app_commands.command(name="check-progress", description="Check your current progress towards completing a goal")
    @app_commands.autocomplete(goal_id=goal_autocomplete)
    async def check_progress(self, interaction : discord.Interaction, goal_id: int):
        """User can check progress towards a specific goal and will send a message with the corresponding data.

        Args:
            interaction: The discord interaction of the user's request.
            goal_id: The goal ID that the user wishes to check progress.

        Raises:
            TODO implement error when the goal does not exist
            implement error for any other sql error
        
        """
        logger.info(f"Received request to check progress of a goal...")

        (progress, percent, reminder) = Goal.check_progress(goal_id)

        await interaction.response.send_message(f"You have completed {progress} which means you are {percent:.2f}% done! Current reminder: {reminder}", ephemeral=True)

    #Command to edit a goal's fields
    @app_commands.command(name="edit-goal", description="Edit a goal you had")
    @app_commands.autocomplete(goal_id=goal_autocomplete)
    async def edit_goal(self, interaction : discord.Interaction, goal_id: int):
        """The user may edit the fields of a goal. Sends a GoalModal for input.

        Args:
            interaction: The discord interaction of the user's request.
            goal_id: The goal ID that the user wishes to check progress.

        Raises:
            TODO implement error when the goal does not exist
            implement error for any other sql error

        TODO call a Goals function instead for high cohesion? Can i do this here?
        TODO make sure that this actually overrides and doesn't just create a new goal on submit
        TODO have previous fields as transparent in the background of modal fields
        
        """
        logger.info("Received request to edit goal...")
        goal_modal = GoalModal() 
        goal_modal.goal_id = goal_id
        await interaction.response.send_modal(goal_modal)

async def setup(bot):
    await bot.add_cog(GoalCog(bot))