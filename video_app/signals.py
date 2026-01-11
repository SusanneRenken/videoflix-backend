"""
Signals for the video_app.

Triggers background video processing after a video
has been successfully created.
"""

import logging

import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import convert_video

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Enqueue video processing task after a new video is created.
    """
    if not created:
        return

    logger.info("---> Video '%s' created. Enqueuing processing task.", instance.title)

    queue = django_rq.get_queue("default")
    queue.enqueue(convert_video, instance.id)
