from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users import views
from apps.users.views import CustomTokenObtainPairView

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.MeView.as_view(), name="me"),
    path("search/", views.UserSearchView.as_view(), name="user-search"),
]
