from dataclasses import dataclass


@dataclass()
class Video:
    title: str
    channel: str
    channel_url: str
    duration: str
    webpage_url: str
    thumbnail: str
