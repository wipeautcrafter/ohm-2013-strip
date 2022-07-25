from threading import Thread
from spotify import Spotify
from render import Render
from util import Timer
import time


song_id = "2w49us5pBD5DfYZ9i31Q82"

class Main:
    def __init__(self):
        self.spotify = Spotify(
            self.on_playback_start,
            self.on_playback_stop,
            self.on_playback_seek)
        
        self.timer = Timer(30)
        self.render = Render()
        self.thread = Thread(target=self.update_loop)
    
        self.exit_flag = False

    def run(self):
        self.running = True
        self.thread.start()

        while not self.exit_flag:
            self.render.render()
            self.timer.sleep()

    def stop(self):
        self.exit_flag = True
        
    def update_loop(self):
        while not self.exit_flag:
            self.spotify.get_playback_update()
            time.sleep(2)
    
    # event listeners
    def on_playback_start(self, song):
        title = song["track"]["name"] + " by " + ", ".join([name for name in song['track']['artists']])
        print(f"Playback: {title}")
        self.render.set_song(song)

    def on_playback_stop(self):
        print("Playback stopped.")
        self.render.set_song()

    def on_playback_seek(self, seek):
        self.render.set_progress(seek["progress"], seek["timestamp"])
        self.render.set_playing(seek["playing"])


if __name__ == "__main__":
    main = Main()
    
    try:
        main.run()
    except (KeyboardInterrupt, SystemExit):
        print("Closing.")
        main.stop()