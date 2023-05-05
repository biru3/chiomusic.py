from dataclasses import dataclass

from music.exceptions import QueueIsEmpty


class PlayList:
    def __init__(self):
        self.queue: list[dict[str: str]] = []

    def is_empty(self) -> bool:
        if self.queue:
            return False
        return True

    def current_music(self) -> None:
        if self.is_empty():
            raise QueueIsEmpty()
        return self.queue[0]

    def add(self, value):
        self.queue.append(value)


@dataclass()
class Music:
    title: str
    author: str
