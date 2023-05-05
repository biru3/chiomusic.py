from discord import Guild, TextChannel
from discord import Interaction
from discord import Embed, Message
from discord import ButtonStyle
from discord.ui import View, Select, Button

from music.playlist import PlayList, Music
from music.emoji import *
from music.exceptions import QueueIsEmpty, NextMusicNotExist


class Server:
    def __init__(self, bot, server: Guild):
        self.bot = bot
        # self.manager = bot.music_manager
        self.server: Guild = server
        self.music_channel: TextChannel | None = None
        self.embed_player: Message | None = None

        self.playlist = PlayList()

        self.play = False

    def set_music_channel(self, embed_player: Message) -> None:
        self.music_channel = embed_player.channel
        self.embed_player = embed_player
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
            embed = Embed(title="노래 예약 기다리는 중!", description="이 채널에 재생하고 싶은 노래의 **제목**이나 **URL**을 입력해주세요", color=0xd4b886)
            placeholder = "예약된 곡이 없어요"
        else:
            if self.play:
                title = "노래를 재생하고 있어요!"
            else:
                title = "노래를 잠시 멈췄어요!"
            current_music = self.playlist.current_music()

            if self.playlist.is_next_exist():
                placeholder = f"다음 곡) {self.playlist[1].title}"
            else:
                placeholder = "다음 곡이 없어요!"

            embed = (
                Embed(title=title, color=0xd4b886)
                .add_field(name="재생중인 노래", value=current_music.title)
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

        if self.play:
            toggle_emoji = BUTTON_PAUSE_EMOJI
            toggle_color = ButtonStyle.green
        else:
            toggle_emoji = BUTTON_PLAY_EMOJI
            toggle_color = ButtonStyle.gray
        button_toggle = Button(
            emoji=toggle_emoji,
            style=toggle_color
        )

        button_next = Button(
            emoji=BUTTON_NEXT_EMOJI,
            style=ButtonStyle.blurple
        )

        async def playlist_callback(interaction: Interaction) -> None:
            selected = playlist_view.values[0]

            if selected == "EmptyPlaylist":
                await interaction.response.send_message("재생할 노래가 없어요! 먼저 노래를 예약해주세요", ephemeral=True,  delete_after=3)
                return
            if selected == "NoNextMusic":
                await interaction.response.send_message("다음 곡이 없어요! 노래를 예약해주세요", ephemeral=True,  delete_after=3)
                return

            self.playlist.jump_to(int(selected))
            await interaction.response.send_message("곡을 넘겼어요!", ephemeral=True,  delete_after=3)

            updated_embed, updated_view = self.get_embed_player()
            await interaction.message.edit(embed=updated_embed, view=updated_view)
            return

        async def button_stop_callback(interaction: Interaction):
            self.play = False
            self.playlist.clear()
            await interaction.response.send_message("안녕히계세요!", ephemeral=True,  delete_after=3)

            updated_embed, updated_view = self.get_embed_player()
            await interaction.message.edit(embed=updated_embed, view=updated_view)
            return

        async def button_toggle_callback(interaction: Interaction):
            if self.playlist.is_empty():
                await interaction.response.send_message("재생할 노래가 없어요! 먼저 노래를 예약해주세요", ephemeral=True,  delete_after=3)
                return

            self.play = not self.play
            if self.play:
                await interaction.response.send_message("노래를 다시 재생할게요!", ephemeral=True,  delete_after=3)
            else:
                await interaction.response.send_message("노래를 멈출게요!", ephemeral=True,  delete_after=3)

            updated_embed, updated_view = self.get_embed_player()
            await interaction.message.edit(embed=updated_embed, view=updated_view)
            return

        async def button_next_callback(interaction: Interaction):
            try:
                self.playlist.next()
            except QueueIsEmpty:
                await interaction.response.send_message("넘길 노래가 없어요!", ephemeral=True,  delete_after=3)
                return
            except NextMusicNotExist:
                self.play = False
                await interaction.response.send_message("다음 노래가 없어, 재생을 중단할게요!", ephemeral=True,  delete_after=3)
            else:
                await interaction.response.send_message("다음 곡을 재생할게요!", ephemeral=True,  delete_after=3)

            updated_embed, updated_view = self.get_embed_player()
            await interaction.message.edit(embed=updated_embed, view=updated_view)
            return

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


