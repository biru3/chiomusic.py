import requests
import youtube_dl
from youtubesearchpython import VideosSearch

from module.youtube.video import Video

YDL_OPTIONS = {
    "extractaudio": True,
    "audioformat": "mp3",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "320k",
    }]}


def youtube_search(arg: str) -> Video:
    try:
        requests.get(arg)
    except: # requests 예외 에러가 너무 많음
        return _keyword_search(arg)
    else:
        return _url_search(arg)


def _url_search(url: str) -> Video:
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            video = ydl.extract_info(url, download=False)
        except youtube_dl.DownloadError:
            raise NotImplementedError("youtube download error")
    return Video(
        title=video["title"],
        channel=video["channel"],
        channel_url=video["channel_url"],
        duration=video["duration"],
        webpage_url=video["webpage_url"],
        thumbnail=video["thumbnail"],
        stream_url=video["formats"][0]["url"]
    )


def _keyword_search(keyword: str) -> Video:
    return _url_search(VideosSearch(keyword, limit=1).result()["result"][0]["link"])


if __name__ == "__main__":
    # video_data = _keyword_search("카라카라")
    # print(video_data)

    video = youtube_search("https://youtube.com/")
    print(video)
