import requests
from django.conf import settings
import hashlib
from urllib.parse import urlencode

class LastFmError(Exception):
    def __init__(self, message,code = None):
        super().__init__(message)
        self.code = code

def handle(r):
    try:
        data = r.json()
    except ValueError:
        r.raise_for_status()
        raise LastFmError("Response was not valid JSON")
    if "error" in data:
        raise LastFmError(data.get("message", "Unknown error"), code=data["error"])
    r.raise_for_status()
    return data

def wrapCall(method, **params):
    params.update({"method": method, "api_key": settings.API_KEY, "format": "json"})
    try:
        r = requests.get(settings.LASTFM_BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        raise LastFmError(str(e))
    return handle(r)

def sign(params):
    items = sorted((k, str(v)) for k, v in params.items() if k not in ("format", "callback"))
    raw = "".join(k + v for k, v in items) + settings.API_SECRET
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def call_signed(method, post=False, **params):
    params.update({"method": method, "api_key": settings.API_KEY})
    params["api_sig"] = sign(params)      
    params["format"] = "json"
    try:
        if post:
            r = requests.post(settings.LASTFM_BASE_URL, data=params, timeout=10)
        else:
            r = requests.get(settings.LASTFM_BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        raise LastFmError(str(e))
    return handle(r)

def auth_url(cb):
    qs = urlencode({"api_key": settings.API_KEY, "cb": cb})
    return f"https://www.last.fm/api/auth/?{qs}" 

def get_session(token):
    return call_signed("auth.getSession",token=token)["session"]

def top_artists_by_country(country, limit=20):
    return wrapCall("geo.getTopArtists", country=country, limit=limit)["topartists"]["artist"]

def top_tracks_by_country(country, limit=20):
    return wrapCall("geo.getTopTracks", country=country, limit=limit)["tracks"]["track"]

def artist_search(artist,limit=20):
    print(wrapCall("artist.search",artist=artist,limit=limit))
    return wrapCall("artist.search",artist=artist,limit=limit)["results"]["artistmatches"]["artist"]

def track_search(track,limit=20):
    return wrapCall("track.search",track=track,limit=limit)["results"]["trackmatches"]["track"]

def album_search(artist,limit=20):
    return wrapCall("album.search",artist=artist,limit=limit)["results"]["albummatches"]["album"]

def update_playing(sk,artist,track,album=None,duration=None):
    params = {"sk": sk, "artist": artist, "track": track}
    if album:
        params["album"] = album
    if duration:
        params["duration"] = duration
    return call_signed("track.updateNowPlaying", post=True, **params)