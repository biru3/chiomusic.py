from discord import Guild, TextChannel, Interaction, Embed
from discord.ui import View, Select

from music.playlist import PlayList, Music


class Server:
    def __init__(self, bot, server: Guild):
        self.bot = bot
        self.manager = bot.music_manager
        self.server: Guild = server
        self.music_channel: TextChannel | None = None
        self.playlist = PlayList()
        self.playlist.queue = [Music(title="title1", author="author1"), Music(title="title2", author="author2")]

    def set_music_channel(self, music_channel: TextChannel) -> None:
        self.music_channel = music_channel
        return

    def is_music_channel_exist(self) -> bool:
        if self.music_channel is None:
            return False
        if self.bot.get_channel(self.music_channel.id) is None:
            self.music_channel = None
            return False
        return True

    def get_embed_player(self) -> (Embed, View):
        if self.playlist.is_empty():
            placeholder = "다음곡이 없어요!"
            current_music = self.playlist.queue[0]

        embed = (
            Embed(title="음악을 재생하고 있어요!")
            .add_field(name="현재 노래", value="[{노래제목}](https://google.com)")
        )

        playlist_view = Select()

        async def playlist_select(interaction: Interaction) -> None:
            selected = playlist_view.values[0]
            await interaction.response.send_message(selected)

        playlist_view.callback = playlist_select
        view = (
            View()
            .add_item(playlist_view)
        )
        return embed, view

    # def send_embed_player(self, channel: TextChannel, interaction: Interaction = None) -> None:
    #     if interaction is None:
    #
