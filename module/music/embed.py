from discord import Message, TextChannel, Embed, ButtonStyle, Interaction, HTTPException
from discord.ui import View, Select, Button

from module.music.playlist import PlayList
from module.music.emoji import *
from module.music.exceptions import QueueIsEmpty, NextMusicNotExist


class EmbedPlayer:
    def __init__(self, server, message: Message = None, channel: TextChannel = None):
        self.bot = server.bot
        self.server = server
        self.playlist: PlayList = server.playlist

        self.message: Message | None = message
        self.channel: TextChannel | None = channel

    def init(self):
        self.channel = None
        self.message = None

    def set(self, channel: TextChannel, message: Message):
        self.channel = channel
        self.message = message
        return

    async def _check_member(self, interaction: Interaction) -> bool:
        if interaction.user.voice is None:
            embed = Embed(
                title="음성 채널에 접속한 후에 노래를 예약해주세요!",
                description="치오와 같은 음성 채널에 접속한 멤버만 이 노래를 예약할 수 있어요",
            )
            await interaction.response.send_message(
                interaction.user.mention, embed=embed, delete_after=3
            )
            return False
        for voice_channel in self.bot.voice_clients:
            if voice_channel.guild == self.server.guild:
                if voice_channel.channel != interaction.user.voice.channel:
                    embed = Embed(
                        title="치오와 같은 음성 채널에 접속한 후에 노래를 예약해주세요!",
                        description="치오와 같은 음성 채널에 접속한 멤버만 이 노래를 예약할 수 있어요",
                    )
                    await interaction.response.send_message(
                        interaction.user.mention, embed=embed, delete_after=3
                    )
                    return False
                else:
                    return True
        return True

    def get(self) -> (Embed, View):
        if self.playlist.is_empty():
            embed = Embed(
                title="노래 예약 기다리는 중!",
                description="이 채널에 재생하고 싶은 노래의 **제목**이나 **URL**을 입력해주세요!",
                color=0xD4B886,
            ).set_image(
                url="https://cdn.discordapp.com/attachments/1086549632882069564/1104730501597646910/IMG_2023_02_02_12_30_21.png"
            )
            placeholder = "예약된 곡이 없어요"
        else:
            if self.server.play:
                title = "노래를 재생하고 있어요!"
            else:
                title = "노래를 잠시 멈췄어요!"
            current_music = self.playlist.current_music()

            if self.playlist.is_next_exist():
                placeholder = f"다음 곡) {self.playlist[1].title}"
            else:
                placeholder = "다음 곡이 없어요!"

            embed = (
                Embed(title=title, color=0xD4B886)
                .add_field(
                    name="재생중인 노래",
                    value=f"[{current_music.title}]({current_music.webpage_url})",
                    inline=False,
                )
                .add_field(
                    name="채널",
                    value=f"[{current_music.channel}]({current_music.channel_url})",
                    inline=True,
                )
                .add_field(name="길이", value=current_music.duration, inline=True)
                .set_image(url=current_music.thumbnail)
            )

        # select
        playlist_view = Select(placeholder=placeholder)
        if self.playlist.is_next_exist():
            for i, music in enumerate(self.playlist[1:]):
                value = str(i + 1)
                label = f"{value}) {music.title}"
                description = f"{music.duration} | {music.channel}"
                playlist_view.add_option(
                    label=label, description=description, value=value
                )
        else:
            if self.playlist.is_empty():
                playlist_view.add_option(label="예약된 곡이 없어요", value="EmptyPlaylist")
            elif not self.playlist.is_next_exist():
                playlist_view.add_option(label="다음 곡이 없어요!", value="NoNextMusic")

        # button
        button_stop = Button(emoji=BUTTON_STOP_EMOJI, style=ButtonStyle.red)

        if self.server.play:
            toggle_emoji = BUTTON_PAUSE_EMOJI
            toggle_color = ButtonStyle.green
        else:
            toggle_emoji = BUTTON_PLAY_EMOJI
            toggle_color = ButtonStyle.gray
        button_toggle = Button(emoji=toggle_emoji, style=toggle_color)

        button_next = Button(emoji=BUTTON_NEXT_EMOJI, style=ButtonStyle.blurple)

        async def playlist_callback(interaction: Interaction) -> None:
            if not await self._check_member(interaction):
                return
            selected = playlist_view.values[0]

            if selected == "EmptyPlaylist":
                await interaction.response.send_message(
                    "재생할 노래가 없어요! 먼저 노래를 예약해주세요", ephemeral=True, delete_after=3
                )
                return
            if selected == "NoNextMusic":
                await interaction.response.send_message(
                    "다음 곡이 없어요! 노래를 예약해주세요", ephemeral=True, delete_after=3
                )
                return

            self.playlist.jump_to(int(selected))
            await interaction.response.send_message(
                "곡을 넘겼어요!", ephemeral=True, delete_after=3
            )
            await self.update()
            return

        async def button_stop_callback(interaction: Interaction):
            if not await self._check_member(interaction):
                return

            self.play = False
            self.playlist.clear()
            await interaction.response.send_message(
                "안녕히계세요!", ephemeral=True, delete_after=3
            )

            await self.update()
            for voice_channel in self.bot.voice_clients:
                if voice_channel.guild == self.server.guild:
                    await voice_channel.disconnect(force=True)
            return

        async def button_toggle_callback(interaction: Interaction):
            if not await self._check_member(interaction):
                return

            if self.playlist.is_empty():
                await interaction.response.send_message(
                    "재생할 노래가 없어요! 먼저 노래를 예약해주세요", ephemeral=True, delete_after=3
                )
                return

            self.play = not self.play
            if self.play:
                await interaction.response.send_message(
                    "노래를 다시 재생할게요!", ephemeral=True, delete_after=3
                )
            else:
                await interaction.response.send_message(
                    "노래를 멈출게요!", ephemeral=True, delete_after=3
                )

            await self.update()
            return

        async def button_next_callback(interaction: Interaction):
            if not await self._check_member(interaction):
                return
            try:
                self.playlist.next()
            except QueueIsEmpty:
                await interaction.response.send_message(
                    "넘길 노래가 없어요! 노래를 다시 예약해주세요", ephemeral=True, delete_after=3
                )
                return
            except NextMusicNotExist:
                self.play = False
                await interaction.response.send_message(
                    "다음 노래가 없어, 재생을 중단할게요!", ephemeral=True, delete_after=3
                )
            else:
                await interaction.response.send_message(
                    "다음 곡을 재생할게요!", ephemeral=True, delete_after=3
                )

            await self.update()
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

    async def update(self):
        embed, view = self.get()
        try:
            await self.message.edit(embed=embed, view=view)
        except HTTPException:
            msg = await self.channel.send(embed=embed, view=view)
            self.message = msg
        return
