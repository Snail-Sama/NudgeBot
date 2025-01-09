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

    @bot.command()
    async def ping(ctx):
        embed = discord.Embed(
            colour=discord.Colour.dark_gold(),
            description="this is the description",
            title="this is the title"
        )

        embed.set_footer(text="this is a footer")
        embed.set_author(name="Snail", url="https://www.youtube.com/watch?v=RrDt9a0q3P0")

        embed.set_thumbnail(url="https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?q=80&w=2376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
        embed.set_image(url="https://plus.unsplash.com/premium_photo-1664299631876-f143dc691c4d?q=80&w=2497&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")

        embed.add_field(name="Snurch", value="https://www.youtube.com/watch?v=RrDt9a0q3P0", inline=False)
        embed.add_field(name="Monkey!", value="https://plus.unsplash.com/premium_photo-1664304287258-f4509f1efb3b?q=80&w=2382&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
        embed.insert_field_at(1, name="Monkey7", value="https://images.unsplash.com/photo-1667831085422-d19fd11acaaa?q=80&w=2574&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
        
        await ctx.send(embed=embed)
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":

    run()