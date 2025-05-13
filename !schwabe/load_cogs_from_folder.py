import discord
from discord.ext import commands
import settings

logger = settings.logging.getLogger("bot") #

def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        for cogs_file in settings.COGS_DIR.glob("*.py"):
            if cogs_file != "__init__.py":
                await bot.load_extension(f"cogs.{cogs_file.name[:-3]}")

    @bot.command(hidden=True)
    async def reload(ctx, cog: str):
        await bot.reload_extension(f"cogs.{cog.lower()}")
    
    @bot.command(hidden=True)
    async def load(ctx, cog: str):
        await bot.load_extension(f"cogs.{cog.lower()}")

    @bot.command(hidden=True)
    async def unload(ctx, cog: str):
        await bot.unload_extension(f"cogs.{cog.lower()}")
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()