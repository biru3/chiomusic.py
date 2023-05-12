from discord import (
    Intents,
    Activity,
    ActivityType,
    Status,
    Message,
    Member,
    Embed,
    ClientException
)
from discord.ext import commands

from module.music.player import MusicPlayerManager
from module.music.exceptions import ServerNotFound
from module.youtube.search import youtube_search


class ChioMusic(commands.Bot):
    def __init__(self):
        self.version = "v2.1.4"

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
        await self.music_manager.load_server()
        return

    async def on_voice_state_update(self, member: Member, before, after):
        if member.bot:
            return
        try:
            server = self.music_manager.get_server(member.guild.id)
        except ServerNotFound:
            return
        for voice_client in self.voice_clients:
            if (
                    voice_client.guild == server.guild
                    and before.channel != after.channel
                    and len(voice_client.channel.members) == 1
            ):
                await voice_client.disconnect(force=True)
                server.playlist.clear()
                await server.update_player()
                embed = Embed(
                    title="다들 어디로 간거죠?",
                    description="음성 채널에 아무도 없어요..플레이리스트를 초기화하고 나가볼게요!",
                )
                await server.get_channel().send(embed=embed, delete_after=3)
        return

    async def on_message(self, message: Message, /) -> None:
        if message.author.bot:
            return
        try:
            server = self.music_manager.get_server(message.guild.id)
        except ServerNotFound:
            print("서버를 찾지 못함")
            return
        if not server.is_music_channel(message.channel):
            print("음악 채널이 아님")
            return
        if message.author.voice is None:
            await message.delete()
            embed = Embed(
                title="음성 채널에 접속한 후에 노래를 예약해주세요!",
                description="치오와 같은 음성 채널에 접속한 멤버만 이 노래를 예약할 수 있어요",
            )
            await message.channel.send(
                message.author.mention, embed=embed, delete_after=3
            )
            return

        # 음성 채널 접속
        # 예외1: 이미 음성 채널에 접속한 경우
        # 예외2: 멤버가 다른 음성 채널에 있는 경우
        try:
            await message.author.voice.channel.connect()
        except ClientException:
            for voice_client in self.voice_clients:
                if voice_client.guild == message.guild:
                    if voice_client.channel != message.author.voice.channel:
                        embed = Embed(
                            title="치오와 같은 음성 채널에 접속한 후에 노래를 예약해주세요!",
                            description="치오와 같은 음성 채널에 접속한 멤버만 이 노래를 예약할 수 있어요",
                        )
                        await message.channel.send(
                            message.author.mention, embed=embed, delete_after=3
                        )
                    else:
                        break
        await message.delete()
        video = await youtube_search(message.content)

        server.playlist.add(video)

        embed = Embed(title="노래를 추가할게요!", description=video.title)
        await message.channel.send(embed=embed, delete_after=3)

        if len(server.playlist) == 1:
            await server.video_stream.play()
            return

        await server.update_player()
        return
