import discord
from discord.ext import commands
from discord import app_commands
import settings, logging, sqlite3, typing

from sqlalchemy import Text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from nudge_bot.db import db
from nudge_bot.utils.logger import configure_logger

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


class Goal(db.Model):
    """Represents a user created goal

    This model maps to the 'goals' table and stores metadata for desired target areas.

    Used in a Flask-SQLAlchemy application for user interaction and data-driven goal operations.
    """

    __tablename__ = "Goals"

    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    target = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Integer, nullable=True, default=0)
    reminder = db.Column(db.String, nullable=True, default='N')

    def validate(self) -> None:
        """Validates the goal instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.

        TODO:
            See about reminder being only a select few options.
        """
        logger.info(f"Validating goal.")
        if not self.title or not isinstance(self.title, str): # execution stops here
            logger.error(f"Title must be a non-empty string. Not {self.title}.")
            raise ValueError("Title must be a non-empty string.")
        else:
            logger.info("else")
        logger.info("does it make it here?")
        if self.description and not isinstance(self.description, str):
            logger.error(f"Goal description must be a string. Not {self.description}.")
            raise ValueError("Goal description must be a string.")
        if self.target is None or not isinstance(self.target, int) or self.target < 0:
            logger.error(f"Target an integer at least 0. Not {self.target}.")
            raise ValueError("Target an integer at least 0.")
        if self.progress is None or not isinstance(self.progress, int) or self.progress < 0:
            logger.error(f"Progress an integer at least 0. Not {self.progress}.")
            raise ValueError("Progress an integer at least 0.")
        if not self.reminder or not isinstance(self.reminder, str):
            logger.error(f"Reminder must be a non-empty string. Not {self.reminder}.")
            raise ValueError("Reminder must be a non-empty string.")
        logger.info(f"Valid goal.")


    @classmethod
    def create_goal(cls, user_id : int, title : str, description : str, target : int, reminder: str) -> str:
        """Create a new goal and add it to the database.

        Args:
            user_id: The id of the user who made the request.
            target: Value the user is trying to reach with their goal.
            description: Description of the user's goal.
            title: Short title of the goal.
            reminder: Frequency of the reminders the user wants to receive.

        Raises:
        
        TODO:
            Add a try except statement for a sql error

        """
        logger.info(f"Inserting goal: user_id - {user_id}, title - {title}, description - {description}, target - {target}, reminder - {reminder}")

        try:
            goal = Goal(
                user_id = user_id,
                title = title,
                description = description,
                target = target,
                progress = 0,
                reminder = reminder
            )
            # goal.validate() # execution stops here when uncommented
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            title=title.strip()
            logger.info(title)
            logger.info(f"Check for existing goal with same compound key (title, target): ({title}, {target})")
            existing = Goal.query.filter_by(title, target=target).first() # execution stops here idk why
            logger.info(existing)
            if existing:
                logger.error(f"Goal {title} - {target} already exists.")
                raise ValueError(f"Goal '{title}' - '{target}' already exists.")
            
            db.session.add(goal)
            db.session.commit()
            logger.info(f"Goal '{title}' - '{target}' successfully added.")

        # Duplicate - do we need this one we might not? Try commenting this out when making unit tests
        except IntegrityError:
            logger.error(f"Goal {title} - {target} already exists.")
            db.session.rollback()
            raise ValueError(f"Goal {title} - {target} already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating goal: {e}")
            db.session.rollback()
            raise 

        # connection = sqlite3.connect("./cogs/goals.db")
        # cursor = connection.cursor()
        # # print("C")
        # print(self.goal_id)
        # if self.goal_id:
        #     # print("A")
        #     cursor.execute("UPDATE Goals SET target = ?, description = ?, progress = ?, title = ?, reminder = ? WHERE goal_id = ?", (target, description, 0, title, reminder, self.goal_id))
        #     action = "updated"
        # else:
        #     # print("B")
        #     cursor.execute("INSERT INTO Goals (user_id, target, description, progress, title, reminder, job) Values (?,?,?,?,?,?,?)", (user_id, target, description, 0, title, reminder, None))
        #     action = "created"

        # connection.commit()
        # connection.close()
        # return action
    
    
    @classmethod
    def delete_goal(cls, goal_id: int):
        """Deletes a goal from the database.

        Args:
            goal_id: ID of the goal to be deleted.

        Raises:
            TODO implement error for goal not found.
        
        TODO:
            implement orm
        """
        logger.info(f"Deleting goal {goal_id}...")

        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Delete goal via goal_id primary key
        cursor.execute("DELETE FROM Goals WHERE goal_id = ?", (goal_id,))

        # Close SQL database connection
        connection.commit()
        connection.close()

        logger.info(f"Successfully deleted goal {goal_id}")


    @classmethod
    def log_goal(cls, goal_id: int, entry: int) -> tuple[bool, str, str]:
        """Logs progress towards a goal in the database.

        Args:
            goal_id: ID of the goal to add progress to.
            entry: Amount to add to progress.

        Returns:
            True if goal has been completed, False if goal has not been completed.
            Title and description of goal.

        Raises:
            TODO implement sql errors

        TODO:
            implement orm
        
        """
        logger.info(f"Logging progress {entry} to goal {goal_id}...")

        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Grab the target and progress values
        cursor.execute("SELECT target, description, progress, title FROM Goals WHERE goal_id = ?", (goal_id,))
        target, description, goal_progress, title = cursor.fetchone()

        #adds entry to what was already there
        goal_progress += entry

        #check if progress has reached target
        if goal_progress >= target:
            #reset progress
            completed = True
            goal_progress = 0
        else:
            completed = False
        
        #update progress in SQL database
        cursor.execute("UPDATE Goals SET progress = ? WHERE goal_id = ?", (goal_progress, goal_id))

        # Close SQL database connection
        connection.commit()
        connection.close()

        logger.info(f"Successfully logged progress towards goal {goal_id}")
        return (completed, title, description)
    
    @classmethod
    def check_progress(cls, goal_id: int) -> tuple[int, float, str]:
        """Check progress of a goal in the database.

        Args:
            goal_id: ID of goal to check progress.

        Returns:
            Progress and percent completed of goal. Current reminder setting (could change this for reminder cog). 
        
        Raises:
            TODO implement sql errors

        TODO:
            ORM

        """
        logger.info(f"Checking progress of goal {goal_id}...")

        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # grabs target and progress from SQL database
        cursor.execute("SELECT target, progress, reminder FROM Goals WHERE goal_id = ?", (goal_id,))
        target, progress, reminder = cursor.fetchone()

        # calculates percent based on progress/target
        percent = (progress / target) * 100

        # Close SQL database connection
        connection.commit()
        connection.close()

        logger.info(f"Successfully retreived progress of goal {goal_id}")
        return (progress, percent, reminder)

# async def setup(bot):
#     await bot.add_cog(GoalCog(bot))