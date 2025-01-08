import discord
from discord.ext import commands
from discord import app_commands
import settings
import typing
import enum

logger = settings.logging.getLogger("bot") 

class Food(enum.Enum):
    apple = 1
    banana = 2
    balls = 3
    kiwi = 4
    cherry = 5

def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        #logger.info(f"Guild ID: {bot.guilds[0].id}")
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)

    @bot.tree.command()
    @app_commands.describe(text_to_send="Simon Says this..")
    @app_commands.rename(text_to_send="message")
    async def say(interaction: discord.Interaction, text_to_send : str):
        await interaction.response.send_message(f"{text_to_send}", ephemeral=True)

    @bot.tree.command()
    async def drink(interaction: discord.Interaction, choice: typing.Literal['milk', 'tea', 'water', 'prime']):
        await interaction.response.send_message(f"You drank {choice}", ephemeral=True)

    @bot.tree.command()
    async def eat(interaction: discord.Interaction, choice: Food):
        await interaction.response.send_message(f"You ate {choice}", ephemeral=True)

    @bot.tree.command()
    @app_commands.choices(choice=[
        app_commands.Choice(name="red", value="1"),
        app_commands.Choice(name="ball", value="2"),
        app_commands.Choice(name="orange", value="3"),
        app_commands.Choice(name="yellow", value="4")
    ])
    async def color(interaction: discord.Interaction, choice:app_commands.Choice[str]):
        await interaction.response.send_message(f"The color you chose was: {choice}", ephemeral=True)
    
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":

    run()