import discord
from discord.ext import commands
from discord import app_commands
import settings
import typing
import enum

logger = settings.logging.getLogger("bot") 


def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        #logger.info(f"Guild ID: {bot.guilds[0].id}")
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)

    async def drink_autocompletion(interaction: discord.Interaction, current : str) -> typing.List[app_commands.Choice[str]]:
        data = []
        for drink_choice in ['milk', 'tea', 'water', 'prime']:
            if current.lower() in drink_choice.lower():
                data.append(app_commands.Choice(name=drink_choice, value=drink_choice))
        return data

    @bot.tree.command()
    @app_commands.autocomplete(choice=drink_autocompletion)
    async def drink(interaction: discord.Interaction, choice: str):
        await interaction.response.send_message(f"You drank {choice}", ephemeral=True)
    
    

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":

    run()