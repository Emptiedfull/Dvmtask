import requests
from django.conf import settings

class LastFmError(Exception):
    def __init__(self, message,code = None):
        super().__init__(message)
        self.code = code

def wrapCall(method,**params):
    params["method"] = method
    params["api_key"] = settings.API_KEY 
    params["format"] = "json"

    try:
        res = requests.get(settings.API_URL,params=params)
        res.raise_for_status()
        data = res.json()
    except (requests.RequestException,ValueError) as e:
        raise LastFmError(str(e))
    if "error" in data:
        raise LastFmError(data.get("message","Invalid error"),code = data["error"])
    if data == {}:
        raise LastFmError("empty response")
    return data

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


    