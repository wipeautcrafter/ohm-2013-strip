import matplotlib.pyplot as plt

from spotify import Spotify
from util import normalize
from render import distance_from_start


# Discotheque - Culture Shock
song_id = "2w49us5pBD5DfYZ9i31Q82"

if __name__ == "__main__":
    spotify = Spotify()
    song = spotify.get_song(song_id)
    
    # fig, ((plot_1), (plot_2)) = plt.subplots(2, 1)

    # # draw timbre / loudness
    # segments = song["analysis"]["segments"]
    # seg_times = [seg["start"] for seg in segments]
    # timbre = normalize([seg["timbre"][0] for seg in segments])
    # plot_1.plot(seg_times, timbre, label="segment timbre")
    # plot_1.legend(loc="upper right")

    # # draw sections with loudness
    # sections = song["analysis"]["sections"]
    # sec_times = [sec["start"] for sec in sections]
    # loudness = normalize([sec["loudness"] + sec["tempo"] for sec in sections])
    # plot_2.plot(sec_times, loudness, label="section energy")
    # plot_2.legend(loc="upper right")

    beats = song["analysis"]["beats"]
    keys = range(0, int(song["track"]["duration"] * 20))
    values = [distance_from_start(k / 20, beats) for k in keys]
    plt.plot(keys, values)
    
    plt.show()
