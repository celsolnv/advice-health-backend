import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "password", "password_confirm"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        """Email deve ser único e em lowercase."""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value

    def validate_first_name(self, value):
        """Nome não pode ser vazio ou só espaços."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("O nome não pode ser vazio.")
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", value):
            raise serializers.ValidationError("O nome deve conter apenas letras.")
        return value

    def validate(self, attrs):
        """Validação cruzada: senhas devem coincidir."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer de leitura — retorna dados do usuário autenticado."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "created_at"]
        read_only_fields = fields

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adiciona dados do usuário na resposta do login."""

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": str(self.user.id),
            "email": self.user.email,
            "first_name": self.user.first_name,
        }

        return data