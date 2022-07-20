from strip import Strip
import credentials
import threading
import colorsys
import spotipy
import random
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
            return None

        return {
            "id": playback["item"]["id"],
            "name": playback["item"]["name"],
            "progress": playback["progress_ms"],
            "duration": playback["item"]["duration_ms"],
            "timestamp": start_time
        }

    def analyse_song(self, track_id) -> None:
        return self.spotify.audio_analysis(track_id)

class Effects:
    def __init__(self) -> None:
        self.strip = Strip()

        self.mode = 0
        self.effect = 0
        self.effect_func = None
        self.beat = 0
        self.beat_even = False

        self.effects = [
            [self.effect_0_0, self.effect_0_1, self.effect_0_2],
            [self.effect_1_0, self.effect_1_1, self.effect_1_2],
            [self.effect_2_0, self.effect_2_1, self.effect_2_2],
            [self.effect_3_0, self.effect_3_1, self.effect_3_2]
        ]

        # debug version for single effect
        # self.effects = [[self.effect_1_2] * 2] * 4

        # variables for effects
        self.hue = 0
        self.hue_step = 360 / self.strip.length

    def set_beat(self):
        self.beat = 1
        self.beat_even = not self.beat_even

    def set_mode(self, mode=None):
        if mode is not None: self.mode = mode
        choices = [(i, v) for i, v in enumerate(self.effects[self.mode])]
        if mode is None: choices.pop(self.effect)
        chosen = random.choice(choices)
        self.effect = chosen[0]
        self.effect_func = chosen[1]

    # util functions
    def get_color(self, i=0, s=1, l=1) -> list[int]:
        hue = ((self.hue + i * self.hue_step) % 360) / 360
        return [int(c * 255) for c in colorsys.hsv_to_rgb(hue, s, l)]

    def increment_hue(self, i) -> None:
        self.hue += i
        if self.hue >= 360:
            self.hue = 0

    # effect functions
    def effect_idle(self):
        for i in range(0, self.strip.length):
            self.strip.set(i, self.get_color(i))
        self.strip.send()
        self.increment_hue(2)

    def effect_0_0(self):
        if self.beat == 1 and self.beat_even:
            self.beat = 0

        for i in range(0, 3):
            self.strip.append(self.get_color(l=self.beat))

        if self.beat > 0.01:
            self.beat /= 2

        self.increment_hue(2)
        self.strip.send()

    def effect_0_1(self):
        if self.beat == 1:
            self.beat = 0
            if self.beat_even:
                self.increment_hue(40)
                self.strip.clear(self.get_color())
            else:
                self.strip.clear(self.get_color(l=0.4))
        self.strip.send()

    def effect_0_2(self):
        if self.beat > 0.05:
            self.beat /= 2

            for i in range(0, self.strip.length):
                self.strip.set(i, self.get_color(i))

        self.increment_hue(40 * self.beat)
        self.strip.send()

    def effect_1_0(self):
        self.strip.fade(.8)
        if self.beat == 1 and self.beat_even:
            self.beat = 0
            self.strip.clear()
            for _i in range(0, 20):
                i = random.randint(0, self.strip.length - 1)
                self.strip.set(i, self.get_color(i))
        self.increment_hue(2)
        self.strip.send()

    def effect_1_1(self):
        if self.beat == 1:
            self.beat = 0

            col = [[0, 0, 0], self.get_color()]
            if self.beat_even: col.reverse()

            self.strip.clear(col[0])
            for i in range(0, int(self.strip.length / 2)):
                self.strip.set(i, col[1])

        self.increment_hue(2)
        self.strip.send()

    def effect_1_2(self):
        self.strip.fade(.8)
        if self.beat == 1:
            self.beat = 0
            self.strip.clear()
            for _i in range(0, 20):
                i = random.randint(0, self.strip.length - 1)
                self.strip.set(i, self.get_color(i))
            for _i in range(0, 20):
                i = random.randint(0, self.strip.length - 1)
                self.strip.set(i, [255, 255, 255])
        self.increment_hue(2)
        self.strip.send()

    def effect_2_0(self):
        if self.beat == 1 and self.beat_even:
            self.increment_hue(5)

        if self.beat > 0.1:
            cols = [self.get_color(0, l=self.beat), self.get_color(self.strip.length / 2, l=self.beat)]
            if self.beat_even: cols.reverse()

            for i in range(0, self.strip.length, 2):
                self.strip.set(i, cols[0])
            for i in range(1, self.strip.length, 2):
                self.strip.set(i, cols[1])

            self.beat /= 2

        self.strip.send()

    def effect_2_1(self):
        if self.beat > 0.1:
            for i in range(0, self.strip.length):
                self.strip.set(i, self.get_color(i / 2, l=self.beat))
            self.beat /= 2

        self.increment_hue(2)
        self.strip.send()

    def effect_2_2(self):
        for i in range(0, 3):
            self.strip.append(self.get_color(l=self.beat))

        if self.beat > 0.01:
            self.beat /= 4

        self.increment_hue(2)
        self.strip.send()

    def effect_3_0(self):
        if self.beat > 0.01:
            self.strip.clear([self.beat * 255] * 3)
            self.beat /= 2
        else:
            l = 0.4 if self.hue == 0 else 0.1
            self.strip.clear(self.get_color(l=l))
            self.hue = 0 if self.hue == 1 else 1

        self.strip.send()

    def effect_3_1(self):
        self.strip.clear([self.beat * 255] * 3 if self.hue == 0 else [0, 0, 0])

        self.hue = 0 if self.hue == 1 else 1
        self.beat /= 2

        self.strip.send()

    def effect_3_2(self):
        cols = [[255 * self.beat] * 3, self.get_color(l=0.1) if self.hue % 2 == 0 else [0, 0, 0]]
        if self.beat_even: cols.reverse()

        for i in range(0, self.strip.length, 2):
            self.strip.set(i, cols[0])
        for i in range(1, self.strip.length, 2):
            self.strip.set(i, cols[1])

        self.increment_hue(3)
        self.beat /= 2

        self.strip.send()

class Visualizer:
    def __init__(self) -> None:
        """
        led effect controller
        """
        self.strip = Strip()
        self.effects = Effects()
        self.playing = False
        self.song = None

    def set_song(self, song):
        self.song = song

    def update(self, beats=None, bars=None, sections=None, playing=True) -> None:
        self.playing = playing

        # update everything if song is playing
        if playing:
            self.sections = sections
            self.beats = beats
            self.bars = bars

            if self.song is not None:
                progress = self.get_progress()
                filtered_sections = [i for i, sec in enumerate(self.sections) if sec["start"] <= progress]
                filtered_beats = [i for i, beat in enumerate(self.beats) if beat["start"] <= progress]
                filtered_bars = [i for i, bar in enumerate(self.bars) if bar["start"] <= progress]
                self.set_section(filtered_sections[-1])
                self.set_beat(filtered_beats[-1])
                self.set_bar(filtered_bars[-1])
            else:
                self.set_section(0)
                self.set_beat(0)
                self.set_bar(0)

    # SET functions
    def set_beat(self, i):
        self.beat = i
        self.beat_next = self.beats[i + 1]["start"] if i + 1 < len(self.beats) else None
        self.effects.set_beat()

    def set_bar(self, i):
        self.bar = i
        self.bar_next = self.bars[i + 1]["start"] if i + 1 < len(self.bars) else None
        if i % 6 == 0:
            self.effects.set_mode()

    def set_section(self, i):
        self.section = i
        self.section_next = self.sections[i + 1]["start"] if i + 1 < len(self.sections) else None
        self.effects.set_mode(self.sections[i]["mode"]) # set mode

    def get_progress(self) -> int:
        return self.song["progress"] / 1000 + time.time() - self.song["timestamp"]

    # run the visualizer forever
    def run(self) -> None:
        while True:
            if self.playing and self.song is not None:
                progress = self.get_progress()

                # skip to next beat
                if self.beat + 1 < len(self.beats) and progress >= self.beat_next:
                    self.set_beat(self.beat + 1)

                # skip to next section
                if self.section + 1 < len(self.sections) and progress >= self.section_next:
                    self.set_section(self.section + 1)

                # skip to next bar
                if self.bar + 1 < len(self.bars) and progress >= self.bar_next:
                    self.set_bar(self.bar + 1)

                self.effects.effect_func()
            else:
                self.effects.effect_idle()

            time.sleep(.05)

class Sections:
    def __init__(self, sections) -> None:
        """
        Parse sections based on their loudness and tempo.
        """
        self.sections = sections

        # filter out the "bad actors"
        self.sections = list(filter(lambda l: l["confidence"] > 0.1, sections))

        # define modes based on acute changes in loudness and tempo
        sorted_sections = list(sorted(enumerate(self.sections), key=lambda k: k[1]["loudness"] + k[1]["tempo"]))

        n_per_mode = int(len(sorted_sections) / 4)
        for i, (n, sec) in enumerate(sorted_sections):
            mode = 3
            if i < n_per_mode: mode = 0
            elif i < n_per_mode * 2: mode = 1
            elif i < n_per_mode * 3: mode = 2
            self.sections[n]["mode"] = mode
        # for i in range(0, len(self.sections)):
        #     mode = 0
        #     if i > 0:
        #         loud_diff = self.sections[i]["loudness"] - self.sections[i - 1]["loudness"]
        #         temp_diff = self.sections[i]["tempo"] - self.sections[i - 1]["tempo"]
        #         if loud_diff > 0.5 or temp_diff > 1: mode = 1
        #         if loud_diff > 1 or temp_diff > 2: mode = 2
        #         if (loud_diff > 3 or temp_diff > 4) and i > 1: mode = 3

        #     self.sections[i]["mode"] = mode

class Watchdog:
    def __init__(self) -> None:
        """
        Synchronize with Spotify.
        """
        self.spotify = Spotify()
        self.visualizer = Visualizer()
        self.thread = None
        self.song_id = 0

    def run(self) -> None:
        self.thread = threading.Thread(target=self.visualizer.run)

        while True:
            song = self.spotify.get_current_song()
            self.visualizer.set_song(song)

            if song is None and self.song_id is not None:
                print("Playback paused.")
                self.visualizer.update(playing=False)
                self.song_id = None

            elif song is not None and song["id"] != self.song_id:
                print(f"Now Playing: {song['name']} ({song['id']})")
                analysis = self.spotify.analyse_song(song["id"])
                sections = Sections(analysis["sections"]).sections

                print("Sections:")
                for s in sections:
                    print(f"- {s['start']}: mode:{s['mode']} loudness:{s['loudness']} tempo:{s['tempo']} confidence:{s['confidence']}")

                self.visualizer.update(analysis["beats"], analysis["bars"], sections)
                self.song_id = song["id"]

            # start thread
            if not self.thread.is_alive():
                self.thread.start()

            time.sleep(2)


if __name__ == "__main__":
    watchdog = Watchdog()
    watchdog.run()
