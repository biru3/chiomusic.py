from discord import app_commands, Interaction, TextChannel
from discord.ext import commands

from module.music.exceptions import ServerNotFound


class ChannelSetter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="음악채널설정", description="음악 채널을 설정합니다")
    @app_commands.describe(channel="음악 채널로 사용할 채널")
    async def command(self, interaction: Interaction, channel: TextChannel) -> None:
        guild_id = interaction.guild_id
        try:
            server = self.bot.music_manager.get_server(guild_id)
        except ServerNotFound:
            server = self.bot.music_manager.add_server(guild_id)

        server.set_music_channel(channel=channel)
        embed, view = server.get_player()
        msg = await channel.send(embed=embed, view=view)
        server.set_music_channel(message=msg)

        await interaction.response.send_message(
            f"{channel.mention} 채널을 음악 예약 채널로 설정했어", ephemeral=True, delete_after=3
        )
        self.bot.music_manager.save_server()
        return


async def setup(bot) -> None:
    await bot.add_cog(ChannelSetter(bot=bot))
    return
