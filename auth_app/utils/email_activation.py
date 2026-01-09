from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User


def send_activation_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_token = default_token_generator.make_token(user)

    activation_link = (f"http://localhost:4200/api/activate/{uid}/{activation_token}/")

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

    return activation_token

def activate_user(uidb64, token):
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