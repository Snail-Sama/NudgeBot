import discord
import random
from discord.ext import commands

import settings
import goal

logger = settings.logging.getLogger("bot") #

def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
    

    @bot.group()
    async def math(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No, {ctx.subcommand_passed} does not belong to math")

    @math.group()
    async def simple(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No, {ctx.subcommand_passed} does not belong to math")

    @simple.command()
    async def add(ctx, x : int, y : int):
        await ctx.send(x + y)
    
    @simple.command()
    async def subtract(ctx, x : int, y : int):
        await ctx.send(x - y)

    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()