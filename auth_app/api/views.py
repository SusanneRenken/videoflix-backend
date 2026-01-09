"""
API views for authentication and account management.

Handles user registration, activation, login, logout,
token refresh, and password reset workflows.
"""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth_app.utils.email_activation import activate_user
from auth_app.utils.reset_password import reset_user_password, send_reset_email
from .serializers import (
    ConfirmPasswordSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
)


class RegistrationView(APIView):
    """
    Register a new user account.

    Creates an inactive user and returns an activation token
    for demonstration purposes.
    """
    
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()

            activation_token = default_token_generator.make_token(saved_account)

            return Response(
                {
                    "user": {
                        "id": saved_account.pk,
                        "email": saved_account.email,
                    },
                    "token": activation_token,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateView(APIView):
    """
    Activate a user account using UID and token.
    """

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = activate_user(uidb64, token)

        if user:
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Activation failed. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(TokenObtainPairView):
    """
    Authenticate a user and set JWT tokens as HTTP-only cookies.
    """

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        refresh = response.data.get("refresh")
        access = response.data.get("access")
        user_data = response.data.get("user")

        secure_flag = not getattr(settings, "DEBUG", False)

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
        )

        response.data = {
            "detail": "Login successful",
            "user": user_data,
        }

        return response


class LogoutView(APIView):
    """
    Log out a user by invalidating the refresh token
    and deleting authentication cookies.
    """

    def post(self, request, *args, **kwargs):
        refresh_cookie = request.COOKIES.get("refresh_token")

        if refresh_cookie:
            try:
                token = RefreshToken(refresh_cookie)
                token.blacklist()
            except TokenError:
                pass

        response = Response(
            {
                "detail": (
                    "Logout successful! All tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response


class RefreshTokenView(TokenRefreshView):
    """
    Refresh the access token using the refresh token cookie.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError):
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")

        response = Response(
            {"detail": "Token refreshed", "access": access_token},
            status=status.HTTP_200_OK,
        )

        secure_flag = not getattr(settings, "DEBUG", False)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
        )

        return response


class PasswordResetView(APIView):
    """
    Send a password reset email if the user exists.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_reset_email(serializer.validated_data["email"])

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK,
        )


class ConfirmPasswordView(APIView):
    """
    Confirm a password reset using UID and token.
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = ConfirmPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = reset_user_password(
            uidb64, token, serializer.validated_data["new_password"]
        )

        if user:
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Password reset failed. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )
