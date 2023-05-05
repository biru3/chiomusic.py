import os

from discord import Intents, Activity, ActivityType, Status
from discord.ext import commands
from dotenv import load_dotenv

from music.player import MusicPlayerManager


class Bot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        super().__init__(command_prefix="", intents=intents, sync_command=True)

        self.exts = ["cogs.set_channel"]

        self.music_manager = MusicPlayerManager(self)

    async def setup_hook(self) -> None:
        """setup sync commands"""
        for ext in self.exts:
            await self.load_extension(ext)
        await self.tree.sync()
        return

    async def on_ready(self) -> None:
        """when bot ready"""
        # change activity to online
        await self.change_presence(
            activity=Activity(
                name="아리 1시간", type=ActivityType.listening, state=Status.online
            )
        )
        return


if __name__ == '__main__':
    load_dotenv()
    discord_api_token = os.environ.get("DiscordApiToken")

    Bot().run(token=discord_api_token)
