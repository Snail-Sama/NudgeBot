import discord
from discord.ext import commands
from discord import app_commands
import typing
import settings

from discord.app_commands import CheckFailure

logger = settings.logging.getLogger("bot")

def is_BotMeister():
    """Checks a user for the BotMeister role before executing certain commands.

    """
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
        """Event triggered when the bot is started up that loads all cogs.
        
        """
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        logger.info(f"Loading cogs...")

        try:
            for cogs_file in settings.COGS_DIR.glob("*.py"):
                if cogs_file.name != "__init__.py":
                    await bot.load_extension(f"nudge_bot.cogs.{cogs_file.name[:-3]}")
        except ValueError as e:
            logger.warning(f"Cogs failed to load: {e}")
            raise
        
        logger.info(f"Cogs successfully loaded!")
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)

    async def cogs_autocompletion(interaction: discord.Interaction, current : str) -> typing.List[app_commands.Choice[str]]:
        """Allows the botmeister to see autocompleted list of cogs.
        
        Returns:
            data containing the list of cogs which are completed by the current string typed
            
        """
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
        """A user with the BotMeister role may reload a cog after making changes so that the whole bot doesn't have to be reloaded.

        Raises:
            CheckFailure: If a user does not have the BotMeister role.
        
        """
        logger.info(f"Received request to reload {choice.lower()}")
        try:
            await bot.reload_extension(f"nudge_bot.cogs.{choice.lower()}")
            await interaction.response.send_message(f"The COG cogs.{choice.lower()} has been reloaded", ephemeral=True)
        except CheckFailure as e:
            await interaction.response.send_message("Not allowed!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unknown error occurred: {e}", ephemeral=True)
            
    
    @bot.tree.command()
    @app_commands.autocomplete(choice=cogs_autocompletion)
    @is_BotMeister()
    async def load(interaction: discord.Interaction, choice: str):
        """User with the BotMeister role may load a new cog after creating a new one in the cogs folder.

        Raises:
            CheckFailure: If a user does not have the BotMeister role.
        
        """
        logger.info(f"Received request to reload {choice.lower()}")
        try:
            await bot.load_extension(f"nudge_bot.cogs.{choice.lower()}")
            await interaction.response.send_message(f"The COG cogs.{choice.lower()} has been loaded", ephemeral=True)
        except CheckFailure as e:
            await interaction.response.send_message("Not allowed!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unknown error occurred: {e}", ephemeral=True)


    @bot.tree.command()
    @app_commands.autocomplete(choice=cogs_autocompletion)
    @is_BotMeister()
    async def unload(interaction: discord.Interaction, choice: str):
        """User with the BotMeister role may unload a cog from the bot.

        Raises:
            CheckFailure: If a user does not have the BotMeister role.
        
        """
        logger.info(f"Received request to unload {choice.lower()}")
        try:
            await bot.unload_extension(f"cogs.{choice.lower()}")
            await interaction.response.send_message(f"The COG cogs.{choice.lower()} has been unloaded", ephemeral=True)
        except CheckFailure as e:
            await interaction.response.send_message("Not allowed!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unknown error occurred: {e}", ephemeral=True)

    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()