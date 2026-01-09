from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from pathlib import Path
from video_app.models import Video
from .serializers import VideoSerializer

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


class VideoListAPIView(generics.ListAPIView):
    queryset = Video.objects.filter(status='ready').order_by('-created_at')
    serializer_class = VideoSerializer


class VideoPlaylistAPIView(APIView):
    def get(self, request, movie_id: int, resolution: str, *args, **kwargs):

        get_ready_video(movie_id)

        video_root = MEDIA_ROOT / "videos" / f"video_{movie_id}" / "processed" / resolution / "index.m3u8"

        if not video_root.exists():
            return Response(status=404)

        return FileResponse(
            video_root.open("rb"),
            content_type="application/vnd.apple.mpegurl"
        )


class VideoSegmentAPIView(APIView):
    def get(self, request, movie_id: int, resolution: str, segment: str, *args, **kwargs):

        get_ready_video(movie_id)

        video_root = MEDIA_ROOT / "videos" / f"video_{movie_id}" / "processed" / resolution / segment

        if not video_root.exists():
            return Response(status=404)

        return FileResponse(
            open(video_root, "rb"),
            content_type="video/MP2T"
        )

def get_ready_video(movie_id: int):
    return get_object_or_404(Video, id=movie_id, status="ready")