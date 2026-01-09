"""
Database models for the video_app.
"""

from django.db import models


class Video(models.Model):
    """
    Represents a video uploaded to the platform.

    Handles metadata, processing status, category assignment,
    and references to stored video and thumbnail files.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("ready", "Ready"),
        ("error", "Error"),
    ]

    CATEGORY_CHOICES = [
        ("drama", "Drama"),
        ("romance", "Romance"),
        ("comedy", "Comedy"),
        ("action", "Action"),
        ("thriller", "Thriller"),
        ("crime", "Crime"),
        ("documentary", "Documentary"),
        ("family", "Family"),
        ("fantasy", "Fantasy"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    original_file = models.FileField(upload_to="videos/originals/")
    thumbnail = models.ImageField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        """
        Return a human-readable representation of the video.
        """
        return self.title
