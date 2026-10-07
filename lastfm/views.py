from django.shortcuts import render
from . import call

def home(request):
    return render(request,"lastfm/home.html")

def top_country(request):
    country = request.GET.get("country","India")
    ctx = {"country":country,"artist_list":[],"tracks_list":[],"error":None }
   
    try:
        ctx["artist_list"] = call.top_artists_by_country(country)
        ctx["track_list"] = call.top_tracks_by_country(country)
    except call.LastFmError as e:
        ctx["error"] = str(e)
    return render(request,"lastfm/top.html",ctx)

def search(request):
    q = request.GET.get("q","").strip()
    kind = request.GET.get("type")
    ctx = {"q":q,"kind":kind,"error":None,"results":None}

    try: 
        match kind:
            case "artist":
                ctx["results"] = call.artist_search(q)
            case "track":
                ctx["results"] = call.track_search(q)
            case "album":
                ctx["results"] = call.album_search(q)
            case _:
                ctx["error"] = "Invalid parameter type, allowed values: artist,album,track "
    except call.LastFmError as e:
        ctx["error"] = str(e)
    return render(request,"lastfm/search.html",ctx)

        