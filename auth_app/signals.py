"""
Signals for the auth_app.

Handles side effects related to user lifecycle events,
such as sending activation emails after registration.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth_app.utils.email_activation import send_activation_email


@receiver(post_save, sender=User)
def send_activation_email_on_registration(sender, instance, created, **kwargs):
    """
    Send an activation email when a new inactive user is created.
    """
    if created and not instance.is_active:
        send_activation_email(instance)
