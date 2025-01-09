import discord
from discord.ext import commands
from discord import app_commands
import settings

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

    @bot.hybrid_command()
    async def pong(ctx):
        await ctx.send("ping")

    @bot.tree.command(description="Welcomes user", name="greetings")
    async def ciao(interaction: discord.Interaction):
        await interaction.response.send_message(f"Ciao! {interaction.user.mention}", ephemeral=True)
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()