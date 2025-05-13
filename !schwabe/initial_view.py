import discord
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.logging.getLogger("bot") 

class SimpleView(discord.ui.View):

    foo : bool = None


    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.message.channel.send("Timedout")
        await self.disable_all_items()
    
    @discord.ui.button(label="Hello",
                       style=discord.ButtonStyle.blurple)
    async def hello(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_message("World")
        self.foo = True
        self.stop()

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.red)
    async def cancel(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_message("Canceling")
        self.foo = False
        self.stop()

def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=".", intents = intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)

    @bot.command()
    async def button(ctx):
        view = SimpleView(timeout=3)
        # button = discord.ui.Button(label="Click me")
        # view.add_item(button)

        message = await ctx.send(view=view)
        view.message = message
        await view.wait()
        await view.disable_all_items()

        if view.foo is None:
            logger.error("Timeout")

        elif view.foo is True:
            logger.error("Ok")

        else:
            logger.error("Cancel")
    
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
    

if __name__ == "__main__":
    run()