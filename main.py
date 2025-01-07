import discord

client = discord.Client()

with open('token.txt') as file:
    token = file.read()

@client.event
async def on_ready():
    print('We have logged in as {0.user}.format(client)')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('.hello'):
        await message.channel.send('shut up :Love:')

client.run(token)