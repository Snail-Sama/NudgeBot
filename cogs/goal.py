import discord
from discord.ext import commands
from discord import app_commands
import typing
import sqlite3
import settings

"""class to handle Modals which gather user input"""
class GoalModal(discord.ui.Modal, title="Enter your goal here!"):
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

    #Inserts user information into goals.db
    #user_id, goal_id, target, description, progress
    #goal_id Primary Key and AUTO-INCREMENT
    def insert_DB(self, user_id : int, target : int, description : str):
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Goals (user_id, target, description, progress) Values (?,?,?,?)", (user_id, target, description, 0))
        connection.commit()
        connection.close()

    #Send a confirmation embed containing submitted information
    async def on_submit(self, interaction : discord.Interaction):
        self.insert_DB(interaction.user.id, self.goal_target.value, self.goal_description.value)

        channel = interaction.guild.get_channel(settings.LOGGER_CH)

        embed = discord.Embed(title="New Goal Set!",
                            description=self.goal_description.value,
                              color=discord.Color.yellow())
        embed.set_author(name=interaction.user.name)
        
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you, {interaction.user.name}", ephemeral=True)

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
    @app_commands.autocomplete(choice='delete_choices')
    async def goal_choices(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[int]]:
        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Fetch goal_ids under a user
        cursor.execute("SELECT goal_id, description FROM Goals WHERE user_id = ?", (interaction.user.id,))
        goal_ids = cursor.fetchall()

        # Close SQL database connection
        connection.close()

        # Create autocomplete choices
        choices = []
        for goal_id, description in goal_ids:
            if current.lower() in description.lower():
                choices.append(app_commands.Choice(name=description, value=goal_id))

        return choices

    #Commmand to delete a goal
    @app_commands.command(name="delete-goal", description="Delete one of you goals")
    @app_commands.autocomplete(goal_id=goal_choices)
    async def delete_goal(self, interaction: discord.Interaction, goal_id: int):
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
    @app_commands.autocomplete(goal_id=goal_choices)
    async def log_goal(self, interaction: discord.Interaction, goal_id: int, new_progress: int):
        # Connect to SQL database
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()

        # Grab the target and progress values
        cursor.execute("SELECT target, description, progress FROM Goals WHERE goal_id = ?", (goal_id,))
        target, description, goal_progress = cursor.fetchone()

        #add new_progress to what was already there
        goal_progress += new_progress

        #check if progress has reached target
        if goal_progress >= target:
            #reset progress
            goal_progress = 0
            
            #create and send completion embed
            channel = interaction.guild.get_channel(settings.LOGGER_CH)
            embed = discord.Embed(title="Completed Goal!",
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
        await interaction.response.send_message(f"Successfully logged {new_progress} progress", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Goal(bot))