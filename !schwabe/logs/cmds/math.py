from discord.ext import commands

@commands.group()
async def math(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f"No, {ctx.subcommand_passed} does not belong to math")

@math.command()
async def add(ctx, x : int, y : int):
    await ctx.send(x + y)
    
async def setup(bot):
    bot.add_command(math)
    bot.add_command(add)