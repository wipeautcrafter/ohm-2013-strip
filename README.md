# ohm-2013-strip
The synchronisation of a generic ohm-2013 strip to Spotify music.

## Installation
```sh
pip install -r requirements.txt # install requirements
python main.py # run script
```

## Configuration
To configure the project, two (2) config files are required:

### config.py
```py
# example for config.py

address = [("192.168.1.255", 6454)] # broadcast or local address
local_host = "0.0.0.0" # localhost address
local_port = 6454 # localhost port
fade = 1 # led brightness (0-1)
length = 50 # length of ledstrip
```

### credentials.py
```py
# example for credentials.py

client_id = "id" # client id for Spotify web
client_secret = "secret" # client secret for Spotify web
username = "username" # to be used Spotify account username

# !! these fields should be left unchanged !!
scopes = ["user-read-playback-state", "user-read-currently-playing"]
redirect_uri = "http://localhost:8888/callback"
```

## Spotify Web API
To make Spotify intergration work, the Spotify web API is used. If [your application](https://developer.spotify.com/dashboard) credentials are correctly stored in the dedicated configuration file, the script should automatically open an authentication page in your browser. After signing in once, the script should have cached your credentials, and should work without repeating this step.
