from django.urls import path, include
from rest_framework import routers
from .view import VideoListAPIView, VideoPlaylistAPIView, VideoSegmentAPIView


urlpatterns = [
    path(
        "video/",
        VideoListAPIView.as_view(),
        name="video-list"
    ),
    path(
        "video/<int:movie_id>/<str:resolution>/index.m3u8",
        VideoPlaylistAPIView.as_view(),
        name="video-playlist"
    ),
    path(
        "video/<int:movie_id>/<str:resolution>/<str:segment>/",
        VideoSegmentAPIView.as_view(),
        name="video-segment"
    ),
]