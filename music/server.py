from discord import Guild, TextChannel, Interaction, Embed, Message
from discord.ui import View, Select

from music.playlist import PlayList, Music


class Server:
    def __init__(self, bot, server: Guild):
        self.bot = bot
        self.manager = bot.music_manager
        self.server: Guild = server
        self.music_channel: TextChannel | None = None
        self.embed_player: Message | None = None
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
            embed_title = "음악 재생을 멈췄어요!"
            embed_value = "없음"
            placeholder = "예약된 곡이 없어요"
        else:
            current_music = self.playlist.current_music()
            embed_title = "음악을 재생하고 있어요!"
            embed_value = f"{current_music.title}"
            placeholder = "다음 곡이 없어요!"
            if self.playlist.is_next_exist():
                placeholder = f"다음 곡) {self.playlist[1].title}"

        embed = (
            Embed(title=embed_title)
            .add_field(name="현재 노래", value=embed_value)
        )

        playlist_view = Select(placeholder=placeholder)
        if self.playlist.is_next_exist():
            for i, music in enumerate(self.playlist[1:]):
                value = str(i + 1)
                label = f"{value}. {music.title}"
                description = music.author
                playlist_view.add_option(label=label, description=description, value=value)
        else:
            if self.playlist.is_empty():
                playlist_view.add_option(label="예약된 곡이 없어요", value="EmptyPlaylist")
            elif not self.playlist.is_next_exist():
                playlist_view.add_option(label="다음 곡이 없어요!", value="NoNextMusic")

        async def playlist_select(interaction: Interaction) -> None:
            selected = playlist_view.values[0]
            self.playlist.jump_to(int(selected))
            updated_embed, updated_view = self.get_embed_player()
            await interaction.message.edit(embed=updated_embed, view=updated_view)
            await interaction.response.send_message("곡을 넘겼어요!", ephemeral=True)
            return

        playlist_view.callback = playlist_select
        view = (
            View()
            .add_item(playlist_view)
        )
        return embed, view
