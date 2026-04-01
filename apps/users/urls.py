from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import CustomTokenObtainPairView
from apps.users import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.MeView.as_view(), name="me"),
]