import time
from util import normalize

class DistanceLayer:
    def __init__(self, items):
        self.items = [(i["start"], i["duration"]) for i in items]

    def value(self, progress):
        filtered = [i for i in self.items if i[0] < progress and i[0] + i[1] > progress]
        if len(filtered) == 0: return 0

        return 1 - (progress - filtered[0][0]) / filtered[0][1]


class Render:
    def __init__(self):
        self.song = None
        self.playing = False
        self.timestamp = None

        self.beat_layer = None

    # set functions
    def set_song(self, song = None):
        self.song = song

        if song is None:
            self.playing = False
        else:
            self.beat_layer = DistanceLayer(self.song["analysis"]["beats"])

    def set_playing(self, playing: bool):
        self.playing = playing

    def set_progress(self, progress: float, timestamp: float):
        self.timestamp = timestamp - progress

    # render functions
    def progress(self):
        return time.time() - self.timestamp

    def render(self):
        # return if there is nothing to be rendered
        if not self.playing:
            return None
        
        t = self.progress()
        v = int(self.beat_layer.value(t) * 40)
        print("[" + (v * "=") + ((40 - v) * " ") + "]")
        # print(t)
        
