from discord import app_commands, Interaction
from discord.ext import commands


class PlayMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="재생", description="노래를 재생해")
    @app_commands.describe(search="영상 링크")
    async def command(self, interaction: Interaction, channel: str):
        return


async def setup(bot) -> None:
    await bot.add_cog(PlayMusic(bot=bot))
    return
