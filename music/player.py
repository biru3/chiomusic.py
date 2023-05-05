from music.server import Server
from music.exceptions import ServerNotFound


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
        new_server = Server(bot=self.bot, server= self.bot.get_guild(server_id))
        self.servers[server_id] = new_server
        return new_server

    def
