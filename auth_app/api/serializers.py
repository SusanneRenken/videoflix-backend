"""
Serializers for authentication and account-related operations.
"""

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Ensures email uniqueness, password confirmation,
    and creates an inactive user account.
    """

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError(
                "Please check your entries and try again."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Please check your entries and try again."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("confirmed_password")

        email = validated_data["email"]
        password = validated_data["password"]

        user = User(
            username=email,
            email=email,
            is_active=False,
        )
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for email-based user authentication.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Account is not activated."
            )

        data = super().validate(
            {
                "username": user.username,
                "password": password,
            }
        )

        data["user"] = {
            "id": user.id,
            "username": user.username,
        }

        return data


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.
    """

    email = serializers.EmailField()


class ConfirmPasswordSerializer(serializers.Serializer):
    """
    Serializer for confirming a new password during reset.
    """

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                "Please check your entries and try again."
            )
        return attrs
