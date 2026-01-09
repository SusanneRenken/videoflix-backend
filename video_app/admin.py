"""
Admin configuration for the video_app.
"""

from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Video model.
    """

    list_display = ("title", "category", "status", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description", "category")
    fields = ("created_at", "title", "description", "category", "original_file")
    readonly_fields = ("created_at", "status")
