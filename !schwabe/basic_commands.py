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

        #bot.tree.copy_global_to(guild=settings.GUILDS_ID)

    @bot.command(
        aliases=['p'],
        help="this is help",
        description="this is a description",
        brief="this is a brief",
        enable=True,
        hidden=False
    )
    async def ping(ctx):
        """ Answers with pong """
        await ctx.send("pong")

    @bot.command()
    async def say(ctx, what = "<:dom:1326268370676486317>"):
        await ctx.send(what)

    bot.command()
    async def say2(ctx, *what):
        await ctx.send(" ".join(what))

    @bot.command()
    async def say3(ctx, what = "<:dom:1326268370676486317>", why = "WHY?"):
        await ctx.send(what + why)
    
    @bot.command()
    async def add(ctx, x : int, y : int):
        await ctx.send(x + y)

    @bot.command()
    async def choices(ctx, *options):
        await ctx.send(random.choice(options))

    @bot.command(
        aliases=['h'],
        help="this is help",
        description="this is a description",
        brief="this is a brief",
        enable=True,
        hidden=True
    )
    async def hello(ctx):
        """ Funny dom """
        await ctx.send('shut up <:dom:1326268370676486317>')

    

    # @bot.command()
    # async def goal(ctx):
    #     await 

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()