import os

from discord import Intents, Activity, ActivityType, Status, Message
from discord.ext import commands
from dotenv import load_dotenv

from module.music.player import MusicPlayerManager
from module.music.exceptions import ServerNotFound
from module.youtube.search import youtube_search


class Bot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
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

    async def on_message(self, message: Message, /) -> None:
        if message.author.bot:
            return
        try:
            server = self.music_manager.get_server(message.guild.id)
        except ServerNotFound:
            return

        video = await youtube_search(message.content)

        server.playlist.add(video)
        await server.update_embed_player()

        await message.reply(video.title, delete_after=3)
        await message.delete(delay=3)

        # 통화방 들어가기
        # 노래 찾기
        # 플레이리스트 추가
        # 노래 스트리밍: task 추가

        return


if __name__ == "__main__":
    load_dotenv()
    discord_api_token = os.environ.get("DiscordApiToken")

    Bot().run(token=discord_api_token)
