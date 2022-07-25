import time
from util import normalize


class Render:
    def __init__(self, song):
        self.song = song
        self.timestamp = time.time()

    def progress(self):
        return time.time() - self.timestamp

    def set_progress(self, progress: float, timestamp: float):
        self.timestamp = timestamp - progress / 1000

    def render(self):
        self.song
