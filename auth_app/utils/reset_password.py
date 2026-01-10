"""
Utilities for password reset via email.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def send_reset_email(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    frontend_base_url = settings.CSRF_TRUSTED_ORIGINS[0]
    reset_link = f"{frontend_base_url}/reset-password/{uid}/{token}/"

    subject = "Reset your Videoflix password"

    text_content = (
        "We received a request to reset your password.\n\n"
        f"{reset_link}\n\n"
        "If you did not request this, please ignore this email."
    )

    html_content = render_to_string(
        "password_reset_email.html",
        {"reset_link": reset_link},
    )

    email_message = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


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
