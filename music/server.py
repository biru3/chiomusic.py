from discord import Guild, TextChannel
from discord import Interaction
from discord import Embed, Message
from discord import ButtonStyle
from discord.ui import View, Select, Button

from music.playlist import PlayList, Music
from music.emoji import *


class Server:
    def __init__(self, bot, server: Guild):
        self.bot = bot
        self.manager = bot.music_manager
        self.server: Guild = server
        self.music_channel: TextChannel | None = None
        self.embed_player: Message | None = None
        self.playlist = PlayList()
        self.playlist.queue = [Music(title=f"title{i}", author=f"author{i}") for i in range(9)]

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

        # embed
        embed = (
            Embed(title=embed_title, color=0xd4b886)
            .add_field(name="현재 노래", value=embed_value)
        )

        # select
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

        # button
        button_stop = Button(
            emoji=BUTTON_STOP_EMOJI,
            style=ButtonStyle.red
        )
        button_toggle = Button(
            emoji=BUTTON_PAUSE_EMOJI,
            style=ButtonStyle.gray
        )
        button_next = Button(
            emoji=BUTTON_NEXT_EMOJI,
            style=ButtonStyle.blurple
        )

        async def playlist_callback(interaction: Interaction) -> None:
            selected = playlist_view.values[0]
            self.playlist.jump_to(int(selected))
            updated_embed, updated_view = self.get_embed_player()
            await interaction.message.edit(embed=updated_embed, view=updated_view)
            await interaction.response.send_message("곡을 넘겼어요!", ephemeral=True)
            return

        async def button_stop_callback(interaction: Interaction):
            await interaction.response.send_message("멈춰!", ephemeral=True)

        async def button_toggle_callback(interaction: Interaction):
            await interaction.response.send_message("토글", ephemeral=True)

        async def button_next_callback(interaction: Interaction):
            await interaction.response.send_message("넘겨!", ephemeral=True)

        playlist_view.callback = playlist_callback
        button_stop.callback = button_stop_callback
        button_toggle.callback = button_toggle_callback
        button_next.callback = button_next_callback

        view = (
            View()
            .add_item(playlist_view)
            .add_item(button_stop)
            .add_item(button_toggle)
            .add_item(button_next)
        )

        return embed, view
