from concurrent.futures import thread
from operator import index, indexOf
import random
from strip import Strip
import credentials
import threading
import colorsys
import spotipy
import time


class Spotify:
    def __init__(self) -> None:
        token = spotipy.util.prompt_for_user_token(
            credentials.username, credentials.scopes, credentials.client_id, credentials.client_secret, credentials.redirect_uri)
        self.spotify = spotipy.Spotify(auth=token)

        self.current_song = None
        self.current_analysis = None

    def get_current_song(self) -> None:
        start_time = time.time()
        playback = self.spotify.current_playback()

        if playback is None or not playback["is_playing"] or playback["item"] is None or playback["item"]["id"] is None:
            return {
                "id": None,
                "name": "Nothing",
                "progress": 0,
                "duration": 0,
                "timestamp": start_time
            }

        return {
            "id": playback["item"]["id"],
            "name": playback["item"]["name"],
            "progress": playback["progress_ms"],
            "duration": playback["item"]["duration_ms"],
            "timestamp": start_time
        }

    def analyse_song(self, track_id) -> None:
        return self.spotify.audio_analysis(track_id)


class Visualizer:
    def __init__(self) -> None:
        self.strip = Strip()
        self.song = None
        self.playing = False
        self.beats = None
        self.sections = None
        self.mode = None

        self.time_per_led = 0.05

        self.hue = 0
        self.hue_step = 360 / self.strip.length

    def get_progress(self) -> int:
        return self.song["progress"] / 1000 + time.time() - self.song["timestamp"]

    def get_color(self, i=0, s=1, l=1) -> list[int]:
        hue = ((self.hue + i * self.hue_step) % 360) / 360
        return [int(c * 255) for c in colorsys.hsv_to_rgb(hue, s, l)]

    def loop(self) -> None:
        while True:
            try:
                progress = self.get_progress()

                beats = self.beats or []
                if len(beats) > 0 and self.playing:
                    sections = list(filter(lambda x: progress > x["start"] and progress < x["start"] + x["duration"], self.sections))
                    if len(sections) > 0: self.mode = sections[0]["mode"]

                    if self.mode == 0: beats = beats[::2] # halve tempo
                    beats = list(filter(lambda x: x["start"] >= progress, beats))

                # idle rgb mode
                if not self.playing:
                    for i in range(0, self.strip.length):
                        self.strip.set(i, self.get_color(i))
                    self.strip.send()

                    self.hue += 2
                    if self.hue > 360:
                        self.hue = 0
                    time.sleep(.05)

                # active spotify synced mode
                elif self.mode == 0:
                    if beats[0]["start"] - progress < self.time_per_led * 2:
                        self.strip.append(self.get_color())
                        self.strip.append(self.get_color())
                        self.strip.append(self.get_color())
                    else:
                        self.strip.append(self.get_color(l=0.01))
                        self.strip.append(self.get_color(l=0.01))
                        self.strip.append(self.get_color(l=0.01))

                    self.strip.send()
                    time.sleep(self.time_per_led)

                elif self.mode == 1:
                    if beats[0]["start"] - progress < self.time_per_led * 2:
                        self.strip.append(self.get_color())
                        self.strip.append(self.get_color())
                        self.strip.append(self.get_color())
                    else:
                        self.strip.append(self.get_color(l=0.005))
                        self.strip.append(self.get_color(l=0.005))
                        self.strip.append(self.get_color(l=0.005))

                    self.strip.send()
                    time.sleep(self.time_per_led)

                elif self.mode == 2:
                    intensity = min(self.time_per_led / (beats[0]["start"] - progress), 1)
                    if intensity > 0.9:
                        self.strip.clear(self.get_color())
                    else:
                        self.strip.clear(self.get_color(l=intensity * 0.2))
                    self.strip.send()
                    time.sleep(.05)

                elif self.mode >= 3:
                    intensity = min(self.time_per_led / (beats[0]["start"] - progress), 1)
                    if intensity > 0.9 and self.mode == 3:
                        self.strip.clear([intensity * 255] * 3)
                    else:
                        self.strip.clear(self.get_color(l=intensity * 0.1))

                    for i in range(0, self.strip.length):
                        if bool(random.randint(0, 15) == 0):
                            self.strip.set(i, self.get_color(i, l=intensity))
                    self.strip.send()
                    time.sleep(.05)

                self.hue += 1
                if self.hue > 360:
                    self.hue = 0
            except:
                pass

# class Effect:
#     def __init__(self, ) -> None:
#         self.

# class Lights:
#     def __init__(self, song, beats, sections, effects) -> None:
#         self.strip = Strip()

#         self.song = song
#         self.beats = beats
#         self.sections = sections
#         self.effects = effects

#         self.beat_index = 0
#         self.beat_end = 0
#         self.section_index = 0
#         self.section_end = 0

#     def get_progress(self) -> int:
#         return self.song["progress"] / 1000 + time.time() - self.song["timestamp"]

#     def next_beat(self) -> None:
#         if self.beat_index >= len(self.beats):
#             self.beat_index = 0
#             self.beat_end = 0
#         self.beat_index += 1


#     def run(self) -> None:
#         while True:
#             while get_progress() < self.next_beat:
#                 self.
#                 time.sleep(0.05)




class Watchdog:
    def __init__(self) -> None:
        self.spotify = Spotify()
        self.visualizer = Visualizer()
        self.thread = None
        self.song_id = None

    def run(self) -> None:
        self.thread = threading.Thread(target=self.visualizer.loop)

        while True:
            song = self.spotify.get_current_song()
            self.visualizer.song = song
            self.visualizer.playing = song["id"] is not None

            if song["id"] != self.song_id:
                print(f"Now Playing: {song['name']} ({song['id']})")

                if song["id"] is not None:
                    analysis = self.spotify.analyse_song(song["id"])
                    self.visualizer.beats = analysis["beats"]
                    self.visualizer.bars = analysis["bars"]

                    # filter out the "bad actors"
                    sections = list(filter(lambda l: l["confidence"] > 0.1, analysis["sections"]))

                    # define modes based on acute changes in loudness and tempo
                    for i in range(0, len(sections)):
                        mode = 0
                        if i > 0:
                            loud_diff = sections[i]["loudness"] - sections[i - 1]["loudness"]
                            temp_diff = sections[i]["tempo"] - sections[i - 1]["tempo"]
                            if loud_diff > 0.5 or temp_diff > 1:
                                mode = 1
                            if loud_diff > 1 or temp_diff > 2:
                                mode = 2
                            if (loud_diff > 2 or temp_diff > 3) and i > 1:
                                mode = 3

                        sections[i]["mode"] = mode

                    self.visualizer.sections = sections

                    # print sections with their modes
                    print("Sections:")
                    for s in sections:
                        print(f"- {s['start']}: mode:{s['mode']} loudness:{s['loudness']} tempo:{s['tempo']} confidence:{s['confidence']}")

                self.song_id = song["id"]

            # start thread
            if not self.thread.is_alive():
                self.thread.start()

            time.sleep(2)


if __name__ == "__main__":
    watchdog = Watchdog()
    watchdog.run()
