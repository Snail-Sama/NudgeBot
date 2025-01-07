import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents = intents)

with open('token.txt') as file:
    token = file.read()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def hello(ctx):
    await ctx.send('shut up <:dom:1326268370676486317>')

bot.run(token)