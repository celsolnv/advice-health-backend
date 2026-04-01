from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import CustomTokenObtainPairSerializer

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