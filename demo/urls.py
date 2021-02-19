# demo/urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^tree/$', views.TreeBarView.as_view(), name='demo'),
    url(r'^historyE/$', views.HistoryEView.as_view(), name='demo'),
    url(r'^historyC/$', views.HistoryCView.as_view(), name='demo'),
    url(r'^historyL/$', views.HistoryLView.as_view(), name='demo'),
    url(r'^index/$', views.IndexView.as_view(), name='demo'),
]
