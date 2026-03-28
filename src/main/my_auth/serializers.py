from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации
    """
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = User
        fields = ("email", "password")
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор входа
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован")
        
        attrs["user"] = user
        return attrs


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Сериализатор запроса авторизации
    """
    class Meta:
        model = User
        fields = ("id", "email", "is_active", "created_at")

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Ваш действующий refresh токен")