"""
Utilities for user account activation via email.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def send_activation_email(user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    backend_base_url = settings.BACKEND_BASE_URL
    activation_link = f"{backend_base_url}/api/activate/{uid}/{token}/"

    subject = "Activate your Videoflix account"

    text_content = (
        "Welcome to Videoflix!\n\n"
        "Please activate your account by clicking the link below:\n\n"
        f"{activation_link}\n\n"
        "If you did not register, you can ignore this email."
    )

    html_content = render_to_string(
        "activation_email.html",
        {
            "user_name": user.username,
            "activation_link": activation_link,
        },
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


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
