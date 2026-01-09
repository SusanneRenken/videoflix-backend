"""
Utilities for user account activation via email.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def send_activation_email(user):
    """
    Send an account activation email to the given user.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_token = default_token_generator.make_token(user)
    frontend_base_url = settings.CSRF_TRUSTED_ORIGINS[0]

    activation_link = (
        f"{frontend_base_url}/api/activate/{uid}/{activation_token}/"
    )

    subject = "Activate your Videoflix account"
    message = (
        "Welcome to Videoflix!\n\n"
        "Please activate your account by clicking the link below:\n\n"
        f"{activation_link}\n\n"
        "If you did not register, you can ignore this email."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def activate_user(uidb64, token):
    """
    Activate a user account if the provided token is valid.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if user.is_active:
        return user

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return user

    return None
