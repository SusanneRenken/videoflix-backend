from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using JWT stored in the `access_token` cookie.

    If the cookie is present, validate it and return (user, token).
    Otherwise fall back to standard header-based authentication.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")

        if not raw_token:
            return super().authenticate(request)

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid or expired access token.")

        return (user, validated_token)