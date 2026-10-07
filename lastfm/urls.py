from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("top/",views.top_country,name="top"),
    path("search/",views.search,name="search"),
]