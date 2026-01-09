from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from auth_app.utils.email_activation import send_activation_email


@receiver(post_save, sender=User)
def send_activation_email_on_registration(sender, instance, created, **kwargs):
    """
    Sends activation email when a new inactive user is created.
    """
    if created and not instance.is_active:
        send_activation_email(instance)