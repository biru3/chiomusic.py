import json

from module.music.server import Server
from module.music.exceptions import ServerNotFound

PATH = "./data/server.json"


class MusicPlayerManager:
    def __init__(self, bot):
        self.bot = bot
        self.servers: dict[int:Server] = {}

    def get_server(self, guild_id: int) -> Server:
        try:
            return self.servers[guild_id]
        except KeyError:
            raise ServerNotFound()

    def add_server(self, server_id: int) -> Server:
        new_server = Server(bot=self.bot, guild=self.bot.get_guild(server_id))
        self.servers[server_id] = new_server
        return new_server

    async def load_server(self):
        with open(PATH, "r") as f:
            data = json.load(f)
        for server_id in data:
            channel_id = data[server_id]
            server = self.add_server(int(server_id))
            channel = self.bot.get_channel(channel_id)
            server.set_music_channel(channel=channel)

            if not server.is_music_channel_exist():
                continue

            await channel.purge(limit=30)

            embed, view = server.get_player()
            message = await channel.send(embed=embed, view=view)

            server.set_music_channel(message=message)
        return

    def save_server(self):
        data = {}
        for server_id, server in self.servers.items():
            data[server_id] = server.get_channel().id
        with open(PATH, "w") as f:
            json.dump(data, f)
        return
