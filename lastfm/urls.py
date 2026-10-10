from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("top/",views.top_country,name="top"),
    path("search/",views.search,name="search"),
    path("lastfm/login/",views.login,name="login"),
    path("lastfm/login/", views.login, name="login"),
path("lastfm/callback/", views.lastfm_cb, name="lastfm_cb"),
path("lastfm/logout/", views.lastfm_logout, name="lastfm_logout"),
path("now-playing/", views.now_playing, name="now_playing"),
]