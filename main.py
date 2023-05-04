from discord import Intents, Activity, ActivityType, Status
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        super().__init__(command_prefix="", intents=intents, sync_command=True)

        self.exts = []

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
                name="명령어", type=ActivityType.listening, state=Status.online
            )
        )
        return
