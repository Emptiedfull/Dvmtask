from django.shortcuts import render,redirect
from django.urls import reverse
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


def login(request):
    cb = request.build_absolute_uri(reverse("lastfm_cb"))
    return redirect(call.auth_url(cb))

def lastfm_cb(request):
    token = request.GET.get("token")
    if not token:
        return render(request,"lastfm/now_playing.html",{"error":"no token recieved"})
    try:
        session = call.get_session(token)
    except call.LastFmError as e:
        return render(request, "lastfm/now_playing.html", {"error": str(e)})

    request.session["lastfm_sk"] = session["key"]
    request.session["lastfm_user"] = session["name"]
    return redirect("now_playing")

def lastfm_logout(request):
    request.session.pop("lastfm_sk", None)
    request.session.pop("lastfm_user", None)
    return redirect("now_playing")

def now_playing(request):
    sk = request.session.get("lastfm_sk")
    ctx = {"user": request.session.get("lastfm_user"), "error": None, "success": None}

    if request.method == "POST" and sk:
        artist = request.POST.get("artist", "").strip()
        track = request.POST.get("track", "").strip()
        album = request.POST.get("album", "").strip()
        if not artist or not track:
            ctx["error"] = "Artist and track are required."
        else:
            try:
                call.update_playing(sk, artist, track, album or None)
                ctx["success"] = f"Now playing: {track} by {artist}"
            except call.LastFmError as e:
                if e.code == 9:       
                    request.session.pop("lastfm_sk", None)
                    request.session.pop("lastfm_user", None)
                    ctx["user"] = None
                    ctx["error"] = "Session expired. Please reconnect."
                else:
                    ctx["error"] = str(e)
    return render(request, "lastfm/now_playing.html", ctx)