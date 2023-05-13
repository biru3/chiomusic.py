import os

from dotenv import load_dotenv

from bot import ChioMusic

if __name__ == "__main__":
    load_dotenv()
    discord_api_token = os.environ.get("DiscordApiToken")

    ChioMusic().run(discord_api_token)
