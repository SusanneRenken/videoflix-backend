
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegistrationSerializer
from auth_app.utils.email_activation import send_activation_email, activate_user


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