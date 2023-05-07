import requests
from youtube_dl import YoutubeDL

from module.youtube.video import Video

YDL_OPTIONS = {"format": "bestvideo+bestaudio", "noplaylist": "True"}


async def youtube_search(arg: str) -> Video:
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            requests.get(arg)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL):
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)["entries"][0]
        else:
            video = ydl.extract_info(arg, download=False)

    return Video.load(video)


if __name__ == "__main__":
    video_data = youtube_search("아리 1시간")
    print(video_data)
