"""
API views for video listing and HLS video delivery.
"""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from video_app.models import Video
from .serializers import VideoSerializer

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


class VideoListAPIView(generics.ListAPIView):
    """
    List all ready-to-play videos ordered by creation date.
    """

    queryset = Video.objects.filter(status="ready").order_by("-created_at")
    serializer_class = VideoSerializer


class VideoPlaylistAPIView(APIView):
    """
    Serve the HLS playlist (index.m3u8) for a given video and resolution.
    """

    def get(self, request, movie_id: int, resolution: str, *args, **kwargs):
        get_ready_video(movie_id)

        playlist_path = (
            MEDIA_ROOT
            / "videos"
            / f"video_{movie_id}"
            / "processed"
            / resolution
            / "index.m3u8"
        )

        if not playlist_path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            playlist_path.open("rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class VideoSegmentAPIView(APIView):
    """
    Serve individual HLS video segments (.ts files).
    """

    def get(self, request, movie_id: int, resolution: str, segment: str, *args, **kwargs):
        get_ready_video(movie_id)

        segment_path = (
            MEDIA_ROOT
            / "videos"
            / f"video_{movie_id}"
            / "processed"
            / resolution
            / segment
        )

        if not segment_path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            segment_path.open("rb"),
            content_type="video/MP2T",
        )


def get_ready_video(movie_id: int):
    """
    Return a ready video object or raise 404 if not found or not ready.
    """
    return get_object_or_404(Video, id=movie_id, status="ready")
