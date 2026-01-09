"""
Utilities for password reset via email.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def send_reset_email(email):
    """
    Send a password reset email to the given email address
    if a matching user exists.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_token = default_token_generator.make_token(user)
    frontend_base_url = settings.CSRF_TRUSTED_ORIGINS[0]

    reset_link = (
        f"{frontend_base_url}/api/reset-password/{uid}/{reset_token}/"
    )

    subject = "Reset your Videoflix password"
    message = (
        "Welcome to Videoflix!\n\n"
        "Please reset your password by clicking the link below:\n\n"
        f"{reset_link}\n\n"
        "If you did not request a password reset, you can ignore this email."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def reset_user_password(uidb64, token, new_password):
    """
    Reset the user's password if the provided token is valid.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return user

    return None
