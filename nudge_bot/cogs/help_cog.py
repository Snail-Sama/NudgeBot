import discord
from discord.ext import commands
import logging

from settings import LOGGER_CH, GUILDS_ID
from nudge_bot.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embedOrange = 0xeab148
    
    async def cog_load(self):
        # sendToChannels = []
        # for guild in self.bot.guilds:
        #     channel = guild.text_channels[0] # send this to the bot commands instead
        #     sendToChannels.append(channel)
        helloEmbed = discord.Embed(
            title="NudgeBot is online",
            description="""Hi, I am NudgeBot! You can type any command after typing my prefix **`'!'`** to activate them. Use **`!help`** to see command options.""",
            colour=self.embedOrange
        )
        # for channel in sendToChannels:
        #     await channel.send(embed=helloEmbed)
        logger.info(LOGGER_CH)
        channel = self.bot.get_channel(LOGGER_CH)
        
        await channel.send(embed=helloEmbed)
    
    @commands.command(
        name="help",
        aliases=["h"],
        help="Provides a description of all specified commmands"
    )
    async def help(self, ctx):
        helpCog = self.bot.get_cog('HelpCog') # do for GoalCog too
        musicCog = self.bot.get_cog('MusicCog')
        commands = helpCog.get_commands() + musicCog.get_commands()

        commandDescription = ""
        for c in commands:
            commandDescription += f"**`!{c.name}`** {c.help}\n"

        commandsEmbed = discord.Embed(
            title="Command List",
            description=commandDescription,
            colour=self.embedOrange
        )

        await ctx.send(embed=commandsEmbed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))