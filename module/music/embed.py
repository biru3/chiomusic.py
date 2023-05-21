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
        return

    async def _check_member(self, interaction: Interaction) -> bool:
        if interaction.user.voice is None:
            embed = Embed(
                title="음성 채널에 접속한 후 노래를 예약해줘.",
                description="나랑 같은 채널에 접속해야 노래를 예약 해줄 수 있어..",
            )
            await interaction.response.send_message(
                interaction.user.mention, embed=embed, delete_after=3
            )
            return False
        for voice_channel in self.bot.voice_clients:
            if voice_channel.guild == self.server.guild:
                if voice_channel.channel != interaction.user.voice.channel:
                    embed = Embed(
                        title="나랑 같은 채널에 접속해야 노래를 예약 해줄 수 있어..",
                        description="나랑 같은 채널에 접속해야 노래를 예약 해줄 수 있어..",
                    )
                    await interaction.response.send_message(
                        interaction.user.mention, embed=embed, delete_after=3
                    )
                    return False
                else:
                    return True
            else:
                # 치오가 존재하는 다른 서버 통화방에 들어가 있을 때
                pass
        return True

    def get(self) -> (Embed, View):
        if self.playlist.is_empty():
            embed = Embed(
                title="노래 예약 기다리는 중!",
                description="이 채널에 재생하고 싶은 노래의 **제목**이나 **URL**을 입력해줘!",
                color=0xD4B886,
            ).set_image(
                url="https://media.discordapp.net/attachments/940520992646787105/1107284992553398364/chio_2.jpg?width=581&height=581"
            )
            placeholder = "예약된 곡이 없어.."
        else:
            if self.server.video_stream.playing:
                title = "노래를 재생하고 있어!"
            else:
                title = "노래를 잠시 멈췄어!"
            current_music = self.playlist.current_music()

            if self.playlist.is_next_exist():
                placeholder = f"다음 곡) {self.playlist[1].title}"
            else:
                placeholder = "다음 곡이 없어!"

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
        embed.set_footer(text=f"chio music {self.bot.version}")

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
                playlist_view.add_option(label="예약된 곡이 없어..", value="EmptyPlaylist")
            elif not self.playlist.is_next_exist():
                playlist_view.add_option(label="다음 곡이 없어..", value="NoNextMusic")

        # button
        button_stop = Button(emoji=BUTTON_STOP_EMOJI, style=ButtonStyle.red)

        if self.server.video_stream.playing:
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
                    "재생할 노래가 없어! 먼저 노래를 예약해야해", ephemeral=True, delete_after=3
                )
                return
            if selected == "NoNextMusic":
                await interaction.response.send_message(
                    "다음 곡이 없어! 노래를 예약해야해", ephemeral=True, delete_after=3
                )
                return

            self.playlist.jump_to(int(selected))
            await interaction.response.send_message(
                "곡을 넘겼어!", ephemeral=True, delete_after=3
            )
            self.server.video_stream.next()
            await self.update()
            return

        async def button_stop_callback(interaction: Interaction):
            if not await self._check_member(interaction):
                return

            self.play = False
            self.playlist.clear()
            await interaction.response.send_message(
                "바이~", ephemeral=True, delete_after=3
            )

            for voice_channel in self.bot.voice_clients:
                if voice_channel.guild == self.server.guild:
                    await voice_channel.disconnect(force=True)
            self.server.video_stream.stop()
            await self.update()
            return

        async def button_toggle_callback(interaction: Interaction):
            if not await self._check_member(interaction):
                return

            if self.playlist.is_empty():
                await interaction.response.send_message(
                    "재생할 노래가 없어! 먼저 노래를 예약해야해", ephemeral=True, delete_after=3
                )
                return

            if not self.server.video_stream.playing:
                await interaction.response.send_message(
                    "노래를 다시 재생할게!", ephemeral=True, delete_after=3
                )
                self.server.video_stream.resume()
            else:
                await interaction.response.send_message(
                    "노래를 멈출게!", ephemeral=True, delete_after=3
                )
                self.server.video_stream.pause()

            await self.update()
            return

        async def button_next_callback(interaction: Interaction):
            if not await self._check_member(interaction):
                return
            try:
                self.playlist.next()
            except QueueIsEmpty:
                await interaction.response.send_message(
                    "넘길 노래가 없어! 노래를 다시 예약해야해", ephemeral=True, delete_after=3
                )
                return
            except NextMusicNotExist:
                await interaction.response.send_message(
                    "다음 노래가 없어, 재생을 중단할게!", ephemeral=True, delete_after=3
                )
                self.server.video_stream.stop()
            else:
                await interaction.response.send_message(
                    "다음 곡을 재생할게!", ephemeral=True, delete_after=3
                )

            self.server.video_stream.next()
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
