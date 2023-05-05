from dataclasses import dataclass

from music.exceptions import QueueIsEmpty, NextMusicNotExist


@dataclass()
class Music:
    title: str
    author: str


class PlayList:
    def __init__(self):
        self.queue: list[Music] = []

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

    def add(self, music: Music):
        self.queue.append(music)

    def next(self) -> Music:
        if self.is_empty():
            raise QueueIsEmpty()
        self.queue.pop(0)
        if self.is_empty():
            raise NextMusicNotExist()
        return self.queue[0]

    def jump_to(self, value: int) -> Music:
        self.queue = self.queue[value:]
        return self.queue[0]

    def clear(self):
        self.queue = []
        return

    def __getitem__(self, item: int) -> Music | list[Music]:
        if self.is_empty():
            raise QueueIsEmpty
        return self.queue[item]
