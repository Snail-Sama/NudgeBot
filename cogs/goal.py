import discord
from discord.ext import commands
from discord import app_commands
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

    """Inserts user information into goals.db
        user_id, goal_id, target, description, progress"""
    def insert_DB(self, user_id : int, target : int, description : str):
        connection = sqlite3.connect("./cogs/goals.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Goals (user_id, target, description, progress) Values (?,?,?,?)", (user_id, target, description, 0))
        connection.commit()
        connection.close()

    """Send a confirmation embed containing submitted information"""
    async def on_submit(self, interaction : discord.Interaction):
        self.insert_DB(interaction.user.id, self.goal_target.value, self.goal_description.value)

        channel = interaction.guild.get_channel(settings.LOGGER_CH)

        embed = discord.Embed(title="New Goal Set!",
                            description=self.goal_description.value,
                              color=discord.Color.yellow())
        embed.set_author(name=interaction.user.name)
        
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you, {self.user.name}", ephemeral=True)

    async def on_error(self, interaction : discord.Interaction, error):
        ...


"""Goal class cog to handle all the goal relate fuctions"""
class Goal(commands.Cog):

    """Creates a user tied goal in the database"""
    @app_commands.command()
    async def set_goal(self, interaction : discord.Interaction):
        goal_modal = GoalModal() 
        await interaction.response.send_modal(goal_modal)

async def setup(bot):
    await bot.add_cog(Goal(bot))