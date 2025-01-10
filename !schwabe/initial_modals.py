import discord
from discord.ext import commands
from discord import app_commands
from discord import utils
import settings

logger = settings.logging.getLogger("bot") 

class FeedBackModal(discord.ui.Modal, title="Send us your feedback"):
    fb_title = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Title",
        required = False,
        placeholder = "Give your feedback a title"
    )
    fb_message = discord.ui.TextInput(
        style = discord.TextStyle.long,
        label = "Message",
        required = False,
        max_length = 500,
        placeholder = "Give your message"
    )

    async def on_submit(self, interaction : discord.Interaction):
        channel = interaction.guild.get_channel(settings.FEEDBACK_CH)

        embed = discord.Embed(title="New Feedback",
                            description=self.fb_message.value,
                              color=discord.Color.yellow())
        embed.set_author(name=self.user.name)

        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you, {self.user.name}", ephemeral=True)

    async def on_error(self, interaction : discord.Interaction, error):
        ...


def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)
        

    @bot.tree.command()
    async def feedback(interaction : discord.Interaction):
        feedback_modal = FeedBackModal()
        feedback_modal.user = interaction.user
        await interaction.response.send_modal(feedback_modal)

    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()