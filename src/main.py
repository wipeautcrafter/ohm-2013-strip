from spotify import Spotify
import time


# Discotheque
song_id = "2w49us5pBD5DfYZ9i31Q82"

def playback_start(song):
    print(song["track"])

def playback_update(player):
    print(player)

def playback_stop():
    print("stopped")

if __name__ == "__main__":
    spotify = Spotify(playback_start, playback_update, playback_stop)

    while True:
        spotify.get_playback_update()
        time.sleep(2)