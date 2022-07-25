import credentials
import spotipy
import time


class Spotify:
    def __init__(self, playback_start, playback_update, playback_stop):
        self.song_id = -1
        self.playback_start = playback_start
        self.playback_update = playback_update
        self.playback_stop = playback_stop

        # oauth2 flow with token caching and refreshing
        self.spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
            client_id=credentials.client_id, client_secret=credentials.client_secret,
            scope=credentials.scopes, redirect_uri=credentials.redirect_uri))

    def get_song(self, id: str):
        """
        Returns a detailed analysis of the given song.
        """
        
        track = self.spotify.track(id)
        features = self.spotify.audio_features([id])[0]
        analysis = self.spotify.audio_analysis(id)

        return {
            # informative track information
            "track": {
                "artists": [a["name"] for a in track["artists"]],
                "duration": track["duration_ms"] / 1000,
                "name": track["name"],
                "id": track["id"],
            },
            
            # information with regards to song features
            "features": {
                "acousticness": features["acousticness"],
                "danceability": features["acousticness"],
                "loudness": features["loudness"],
                "valence": features["valence"],
                "energy": features["energy"],
                "tempo": features["tempo"],
            },

            # song fade in and out timings
            "fade": {
                "out": analysis["track"]["start_of_fade_out"],
                "in": analysis["track"]["end_of_fade_in"],
            },

            # song analysis timestamps
            "analysis": {
                "segments": analysis["segments"],
                "sections": analysis["sections"],
                "tatums": analysis["tatums"],
                "beats": analysis["beats"],
                "bars": analysis["bars"],
            },
        }

    def get_playback_update(self):
        """
        Run callback functions if playback has updated.
        """

        current = self.spotify.current_playback()
        new_id = current["item"]["id"] if current and current["item"] else None

        if new_id is not None:
            if new_id != self.song_id:
                song = self.get_song(new_id)
                self.playback_start(song)
        
            self.playback_update({
                "progress": current["progress_ms"] / 1000,
                "playing": current["is_playing"],
                "timestamp": time.time(),
            })

        elif new_id != self.song_id:
                self.playback_stop()
        
        self.song_id = new_id