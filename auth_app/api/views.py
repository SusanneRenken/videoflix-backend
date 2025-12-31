from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import RegistrationSerializer, LoginSerializer, PasswordResetSerializer, ConfirmPasswordSerializer
from auth_app.utils.email_activation import send_activation_email, activate_user
from auth_app.utils.reset_password import send_reset_email, reset_user_password


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        user = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            activation_token = send_activation_email(saved_account)

            user = {
                'id': saved_account.pk,
                'email': saved_account.email,
            }
            return Response(
                {
                    'user': user,
                    'token': activation_token,
                }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class ActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = activate_user(uidb64, token)

        if user is not None:
            return Response(
                {'message': 'Account successfully activated.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Activation failed. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(TokenObtainPairView):
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

    def post(self, request, *args, **kwargs):
        refresh_cookie = request.COOKIES.get("refresh_token")

        if refresh_cookie:
            try:
                token = RefreshToken(refresh_cookie)
                token.blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response


class RefreshTokenView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"detail": "Refresh token invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = serializer.validated_data.get("access")

        response = Response(
            {
                "detail": "Token refreshed",
                "access": access_token,
            },
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
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        send_reset_email(email)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )


class ConfirmPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):

        serializer = ConfirmPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]

        user = reset_user_password(uidb64, token, new_password)

        if user is not None:
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Password reset failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )