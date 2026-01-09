"""
Custom JWT authentication using HTTP-only cookies.

Falls back to header-based JWT authentication if no cookie is present.
"""

from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate requests using a JWT stored in the `access_token` cookie.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")

        if not raw_token:
            return super().authenticate(request)

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except (InvalidToken, TokenError):
            raise exceptions.AuthenticationFailed(
                "Invalid or expired access token."
            )

        return user, validated_token
