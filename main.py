import os

from discord import Intents, Activity, ActivityType, Status, Message, Member
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

    async def on_voice_state_update(self, member: Member, before, after):
        if member.bot:
            return
        try:
            server = self.music_manager.get_server(member.guild.id)
        except ServerNotFound:
            return
        for voice_channel in self.voice_clients:
            if voice_channel.guild == server.guild and before.channel != after.channel and len(voice_channel.channel.members) == 1:
                await voice_channel.disconnect(force=True)
                server.playlist.clear()
                await server.update_player()
                await server.get_channel().send("통화방에 아무도 없는 관계로... 이만 나는 플레이리스트를 초기화하고 나가보도록하지", delete_after=3)
        return

    async def on_message(self, message: Message, /) -> None:
        if message.author.bot:
            return
        try:
            server = self.music_manager.get_server(message.guild.id)
        except ServerNotFound:
            return
        if not server.is_music_channel(message.channel):
            return
        if message.author.voice is None:
            await message.delete()
            await message.channel.send(f"{message.author.mention} 씨발아 통방에는 들어가서 예약해야지", delete_after=3)
            return

        await message.author.voice.channel.connect()

        video = await youtube_search(message.content)

        server.playlist.add(video)
        await server.update_player()

        await message.delete()
        await message.channel.send(video.title, delete_after=3)

        # 통화방 들어가기
        # 노래 찾기
        # 플레이리스트 추가
        # 노래 스트리밍: task 추가

        return


if __name__ == "__main__":
    load_dotenv()
    discord_api_token = os.environ.get("DiscordApiToken")

    Bot().run(token=discord_api_token)
