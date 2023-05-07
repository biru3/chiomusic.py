import requests
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

from module.youtube.video import Video

# YDL_OPTIONS = {
#     "extractaudio": True,
#     "audioformat": "mp3",
#     "postprocessors": [{
#         "key": "FFmpegExtractAudio",
#         "preferredcodec": "mp3",
#         "preferredquality": "320k",
#     }]}


async def youtube_search(arg: str) -> Video:
    return _keyword_search(keyword=arg)


# def _url_search(url: str) -> Video:
#     with YoutubeDL(YDL_OPTIONS) as ydl:
#         video = ydl.extract_info(url, download=False)
#         print(video)
#     return Video(
#         title=video["title"],
#         upload_date=video["upload_date"],
#         uploader=video["uploader"],
#         uploader_url=video["uploader_url"],
#         channel_url=video["channel_url"],
#         duration=video["duration"],
#         view_count=video["view_count"],
#         webpage_url=video["webpage_url"],
#         thumbnail=video["thumbnail"],
#     )


def _keyword_search(keyword: str) -> Video:
    video = VideosSearch(keyword, limit=1).result()["result"][0]
    return Video(
        title=video["title"],
        channel=video["channel"]["name"],
        channel_url=video["channel"]["link"],
        duration=video["duration"],
        webpage_url=video["link"],
        thumbnail=video["thumbnails"][0]["url"]
    )


if __name__ == "__main__":
    video_data = _keyword_search("카라카라")
    print(video_data)
