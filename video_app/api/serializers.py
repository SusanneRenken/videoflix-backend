"""
Serializers for video-related API responses.
"""

from rest_framework import serializers

from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for video objects used in the video dashboard.
    """

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]
        read_only_fields = ["id", "created_at", "thumbnail_url"]

    def get_thumbnail_url(self, obj):
        """
        Return the absolute URL of the video's thumbnail if available.
        """
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
