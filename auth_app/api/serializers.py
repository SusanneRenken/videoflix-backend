from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password', 'is_active']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError(
                'Please check your entries and try again.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Please check your entries and try again.')
        return value

    def create(self, validated_data):
        validated_data.pop("confirmed_password")

        email = validated_data["email"]
        password = validated_data["password"]

        user = User(
            username=email,
            email=email,
            is_active=False
        )
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

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
        
        if user.is_active == False:
            raise serializers.ValidationError(
                "Account is not activated."
            )

        data = super().validate({"username": user.username, "password": password})

        data["user"] = {
            "id": user.id,
            "username": user.username,
        }

        return data
