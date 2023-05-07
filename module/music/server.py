from discord import Guild, Embed, Message, TextChannel
from discord.ui import View

from module.music.playlist import PlayList
from module.music.embed import EmbedPlayer


class Server:
    def __init__(self, bot, guild: Guild):
        self.bot = bot
        # self.manager = bot.music_manager
        self.guild: Guild = guild
        self.playlist = PlayList()
        self.embed_player: EmbedPlayer = EmbedPlayer(self)

        self.play = False

    def set_music_channel(self, message: Message) -> None:
        self.embed_player.set(message.channel, message)
        return

    def is_music_channel_exist(self) -> bool:
        if self.embed_player.channel is None:
            return False
        if self.bot.get_channel(self.embed_player.channel.id) is None:
            self.embed_player.init()
            return False
        return True

    def is_music_channel(self, channel: TextChannel) -> bool:
        if channel == self.embed_player.channel:
            return True
        return False

    def get_player(self) -> (Embed, View):
        return self.embed_player.get()

    def get_channel(self) -> TextChannel:
        return self.embed_player.channel

    async def update_player(self):
        await self.embed_player.update()
        return
