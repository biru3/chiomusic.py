from dataclasses import dataclass


@dataclass()
class Video:
    title: str
    description: str
    upload_date: str
    uploader: str
    uploader_url: str
    channel_url: str
    duration: int
    view_count: int
    webpage_url: str
    thumbnail: str

    @classmethod
    def load(cls, json: dict):
        return cls(
            title=json["title"],
            description=json["description"],
            upload_date=json["upload_date"],
            uploader=json["uploader"],
            uploader_url=json["uploader_url"],
            channel_url=json["channel_url"],
            duration=json["duration"],
            view_count=json["view_count"],
            webpage_url=json["webpage_url"],
            thumbnail=json["thumbnail"],
        )
