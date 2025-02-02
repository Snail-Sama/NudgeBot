import discord
from discord.ext import commands
from discord import app_commands
import typing
import settings

logger = settings.logging.getLogger("bot")

def is_BotMeister():
    def predicate(interaction : discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name="BotMeister") # Get the role
        if role in interaction.user.roles:
            return True
    return app_commands.check(predicate)

def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        for cogs_file in settings.COGS_DIR.glob("*.py"):
            if cogs_file.name != "__init__.py":
                await bot.load_extension(f"cogs.{cogs_file.name[:-3]}")
        
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)

    async def cogs_autocompletion(interaction: discord.Interaction, current : str) -> typing.List[app_commands.Choice[str]]:
        cogs = [cogs_file for cogs_file in settings.COGS_DIR.glob("*.py") if cogs_file.name != '__init__.py']
        data = []
        for cog in cogs:
            if current.lower() in cog.stem:
                data.append(app_commands.Choice(name=cog.stem, value=cog.stem))
        return data
    
    @bot.tree.command()
    @app_commands.autocomplete(choice=cogs_autocompletion)
    @is_BotMeister()
    async def reload(interaction: discord.Interaction, choice: str):
        await bot.reload_extension(f"cogs.{choice.lower()}")
        await interaction.response.send_message(f"The COG cogs.{choice.lower()} has been reloaded", ephemeral=True)
    
    @reload.error
    async def reload_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed!", ephemeral=True)
    
    @bot.tree.command()
    @app_commands.autocomplete(choice=cogs_autocompletion)
    @is_BotMeister()
    async def load(interaction: discord.Interaction, choice: str):
        await bot.load_extension(f"cogs.{choice.lower()}")
        await interaction.response.send_message(f"The COG cogs.{choice.lower()} has been loaded", ephemeral=True)

    @load.error
    async def load_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed!", ephemeral=True)

    @bot.tree.command()
    @app_commands.autocomplete(choice=cogs_autocompletion)
    @is_BotMeister()
    async def unload(interaction: discord.Interaction, choice: str):
        await bot.unload_extension(f"cogs.{choice.lower()}")
        await interaction.response.send_message(f"The COG cogs.{choice.lower()} has been unloaded", ephemeral=True)

    @unload.error
    async def unload_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed!", ephemeral=True)
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()