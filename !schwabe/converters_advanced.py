import discord
import random
from discord.ext import commands

import settings
import goal

logger = settings.logging.getLogger("bot") #

class Slapper(commands.Converter):
    use_nicknames : bool

    def __init__(self, *, use_nicknames) -> None:
        self.use_nicknames = use_nicknames

    async def convert(self, ctx, argument):
        someone = random.choice(ctx.guild.members)
        nickname = ctx.author
        if self.use_nicknames and ctx.author.nick != None:
            nickname = ctx.author.nick
            
        return f"{nickname} slaps {someone} with {argument}"

def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        #bot.tree.copy_global_to(guild=settings.GUILDS_ID)
    
    @bot.command()
    async def add(ctx, x : int, y : int):
        await ctx.send(x + y)

    @bot.command()
    async def joined(ctx, who : discord.Member):
        await ctx.send(who.joined_at)

    @bot.command()
    async def slap(ctx, reason : Slapper(use_nicknames=True) ):
        await ctx.send(reason)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()