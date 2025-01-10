import discord
from discord.ext import commands
from discord import app_commands
import settings
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")
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
    async def motivate(ctx):
        prompt = "Generate a motivational quote about success and perseverance."
        response = generator(prompt, max_length=50, num_return_sequences=1, truncation=True)
        message = response[0]['generated_text']
        message = message[len(prompt):].strip()
        await ctx.send(f"{message}")
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()