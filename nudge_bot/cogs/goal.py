import discord
from discord.ext import commands
from discord import app_commands
import typing
import sqlite3
import settings
import schedule

"""class to handle Modals which gather user input"""
class GoalModal(discord.ui.Modal, title="Enter your goal here!"):
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

    #Inserts user information into goals.db
    #user_id, goal_id, target, description, progress, title
    #goal_id Primary Key and AUTO-INCREMENT
    def insert_DB(self, user_id : int, target : int, description : str, title : str, reminder: str) -> str:
        """Insert a new goal into the DB

        Args:
            user_id: The id of the user who made the request.
            target: Value the user is trying to reach with their goal.
            description: Description of the user's goal.
            title: Short title of the goal.
            reminder: Frequency of the reminders the user wants to receive.

        Returns:
            String describing the action done on the database.

        Raises:
        
        TODO:
            Add a try except statement for a sql error
            Add logging
            Move to sql utils? check if already exists

        """
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()
        # print("C")
        print(self.goal_id)
        if self.goal_id:
            # print("A")
            cursor.execute("UPDATE Goals SET target = ?, description = ?, progress = ?, title = ?, reminder = ? WHERE goal_id = ?", (target, description, 0, title, reminder, self.goal_id))
            action = "updated"
        else:
            # print("B")
            cursor.execute("INSERT INTO Goals (user_id, target, description, progress, title, reminder, job) Values (?,?,?,?,?,?,?)", (user_id, target, description, 0, title, reminder, None))
            action = "created"

        connection.commit()
        connection.close()
        return action

    #Send a confirmation embed containing submitted information
    async def on_submit(self, interaction : discord.Interaction):
        """Asynchronous method for when users submit their goal information in thte modal.

        Args:
            interaction: The discord interaction of the user's request.

        Awaits:
            Sending a message in the corresponding channel.

        Raises:
        
        TODO:
            Add a try except statement for a sql error
            Add logging
            Move to sql utils? check if already exists

        """
        # print("D")
        action = self.insert_DB(interaction.user.id, self.goal_target.value, self.goal_description.value, self.goal_title.value, "N")
        channel = interaction.guild.get_channel(settings.LOGGER_CH)

        embed = discord.Embed(title=self.goal_title.value,
                              description=self.goal_description.value,
                              color=discord.Color.yellow())
        embed.set_author(name=interaction.user.name)

        await channel.send(embed=embed)
        await interaction.response.send_message(f"Succesfully {action} goal!", ephemeral=True)

    async def on_error(self, interaction : discord.Interaction, error):
        ...


"""Goal class cog to handle all the goal relate fuctions"""
class Goal(commands.Cog):

    # Command to set/create a new goal
    @app_commands.command(name="create-goal", description="Set a new goal!")
    async def set_goal(self, interaction : discord.Interaction):
        goal_modal = GoalModal() 
        await interaction.response.send_modal(goal_modal)

    # Function to fetch all the goal_ids linked with user_id for autocomplete
    async def goal_choices(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[int]]:
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

    #Commmand to delete a goal
    @app_commands.command(name="delete-goal", description="Delete one of you goals")
    @app_commands.autocomplete(goal=goal_choices)
    async def delete_goal(self, interaction: discord.Interaction, goal: int):
        goal_id = goal
        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Delete goal via goal_id primary key
        cursor.execute("DELETE FROM Goals WHERE goal_id = ?", (goal_id,))

        # Close SQL database connection
        connection.commit()
        connection.close()

        # Send success message
        await interaction.response.send_message(f"Successfully deleted goal", ephemeral=True)

    #Command to log progress towards a goal
    @app_commands.command(name="log", description="log progress towards a goal")
    @app_commands.autocomplete(goal=goal_choices)
    async def log_goal(self, interaction: discord.Interaction, goal: int, entry: int):
        goal_id = goal
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
            goal_progress = 0
            
            #create and send completion embed
            channel = interaction.guild.get_channel(settings.LOGGER_CH)
            embed = discord.Embed(title=f"Completed {title}",
                            description=description,
                              color=discord.Color.brand_green())
            embed.set_author(name=interaction.user.name)
            await channel.send(embed=embed)
        
        #update progress in SQL database
        cursor.execute("UPDATE Goals SET progress = ? WHERE goal_id = ?", (goal_progress, goal_id))

        # Close SQL database connection
        connection.commit()
        connection.close()

        # Send success message
        await interaction.response.send_message(f"Successfully logged {entry} to your progress", ephemeral=True)

    #Command to check current progress towards a goal
    @app_commands.command(name="check-progress", description="Check your current progress towards completing a goal")
    @app_commands.autocomplete(goal=goal_choices)
    async def check_goal_progress(self, interaction : discord.Interaction, goal: int):
        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # grabs target and progress from SQL database
        cursor.execute("SELECT target, progress, reminder FROM Goals WHERE goal_id = ?", (goal,))
        target, progress, reminder = cursor.fetchone()

        # calculates percent based on progress/target
        percent = (progress / target) * 100

        # Close SQL database connection
        connection.commit()
        connection.close()

        await interaction.response.send_message(f"You have completed {progress} which means you are {percent:.2f}% done! Current reminder: {reminder}", ephemeral=True)

    #Command to edit a goal's fields
    @app_commands.command(name="edit-goal", description="Edit a goal you had")
    @app_commands.autocomplete(goal=goal_choices)
    async def edit_goal(self, interaction : discord.Interaction, goal: int):
        goal_modal = GoalModal() 
        goal_modal.goal_id = goal
        await interaction.response.send_modal(goal_modal)

async def setup(bot):
    await bot.add_cog(Goal(bot))