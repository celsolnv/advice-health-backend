from django.db import models
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.models import User
from apps.users.serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    """Endpoint público para criação de novos usuários."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """Retorna os dados do usuário autenticado. Rota protegida."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()

        return User.objects.filter(models.Q(email__icontains=query) | models.Q(first_name__icontains=query)).exclude(
            id=self.request.user.id
        )
