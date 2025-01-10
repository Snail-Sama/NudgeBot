import discord
from discord.ext import commands
from discord import app_commands
from discord import utils
import settings

class Frequency_Select(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="2x Daily", value="2D"),
            discord.SelectOption(label="1x Daily", value="1D"),
            discord.SelectOption(label="Weekly", value="W"),
            discord.SelectOption(label="Monthy", value="M"),
            discord.SelectOption(label="None", value="N"),
        ]
        super().__init__(options=options, placeholder="Would you like a reminder?")

    async def callback(self, interaction:discord.Interaction):
        await self.view.respond_to_answer(interaction, self.values)

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.answer = None
        self.add_item(Frequency_Select())

    async def respond_to_answer(self, interaction:discord.Integration, choices):
        self.answer = choices
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()

class Reminder(commands.Cog):
    @app_commands.command(name="set_reminder", description = "Set your reminder!")
    async def set_reminder(self, interaction: discord.Interaction):
        view = DropdownView()
        await interaction.response.send_message(view=view)

        await view.wait()
        results = {
            "a": view.answer,
        }

        # print(results)
        await interaction.followup.send(f"{results}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminder(bot))