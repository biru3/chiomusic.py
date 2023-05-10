import asyncio

from discord import FFmpegPCMAudio

from module.music.playlist import PlayList
from module.music.exceptions import NextMusicNotExist, QueueIsEmpty

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


class VideoStream:
    def __init__(self, server, playlist):
        self.playing = False
        self.skip = False

        self.server = server
        self.playlist: PlayList = playlist

        self.queue_empty_timer = 0

    async def run(self):
        while True:
            if self.server.guild.voice_client is None:
                return

            if self.skip:
                self.skip = False
                self.server.guild.voice_client.stop()
                try:
                    video = self.playlist.current_music()
                    self.server.guild.voice_client.play(FFmpegPCMAudio(video.stream_url, executable="ffmpeg.exe", **FFMPEG_OPTIONS))
                except QueueIsEmpty:
                    return

            if not self.server.guild.voice_client.is_playing() and not self.server.guild.voice_client.is_paused():
                try:
                    self.playlist.next()
                except NextMusicNotExist:
                    return
                except QueueIsEmpty:
                    while True:
                        await asyncio.sleep(1)
                        self.queue_empty_timer += 1
                        if self.queue_empty_timer >= 300:
                            await self.server.guild.voice_client.disconnect()
                else:
                    video = self.playlist.current_music()
                    self.server.guild.voice_client.play(FFmpegPCMAudio(video.stream_url, executable="ffmpeg.exe", **FFMPEG_OPTIONS))
                    await self.server.update_player()
            await asyncio.sleep(1)

    async def play(self):
        self.playing = True
        video = self.playlist.current_music()
        self.server.guild.voice_client.play(FFmpegPCMAudio(video.stream_url, executable="ffmpeg.exe", **FFMPEG_OPTIONS))
        await self.server.update_player()
        await self.run()
        return

    def pause(self):
        self.playing = False
        self.server.guild.voice_client.pause()
        return

    def resume(self):
        self.playing = True
        self.server.guild.voice_client.resume()
        return

    def stop(self):
        self.playing = False
        self.server.guild.voice_client.stop()
        return

    def next(self):
        self.skip = True
        return