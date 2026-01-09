"""
App configuration for the video_app.

Ensures that video-related Django signals are registered
when the application is ready.
"""

from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    name = "video_app"

    def ready(self):
        import video_app.signals  # noqa: F401
