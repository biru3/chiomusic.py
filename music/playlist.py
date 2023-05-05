from dataclasses import dataclass

from music.exceptions import QueueIsEmpty


@dataclass()
class Music:
    title: str
    author: str


class PlayList:
    def __init__(self):
        self.queue: list[dict[str: str]] = []

    def is_empty(self) -> bool:
        if self.queue:
            return False
        return True

    def is_next_exist(self) -> bool:
        if len(self.queue) <= 1:
            return False
        return True

    def current_music(self) -> Music:
        if self.is_empty():
            raise QueueIsEmpty()
        return self.queue[0]

    def add(self, value):
        self.queue.append(value)

    def next(self) -> Music:
        self.queue.pop(0)
        return self.queue[0]

    def jump_to(self, value: int) -> Music:
        self.queue = self.queue[value:]
        return self.queue[0]

    def __getitem__(self, item: int) -> Music | list[Music]:
        if self.is_empty():
            raise QueueIsEmpty
        return self.queue[item]
