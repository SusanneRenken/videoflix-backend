from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print("Video post-save signal triggered.")
    if created:
        print(f"Video '{instance.title}' has been saved. Created: {created}")