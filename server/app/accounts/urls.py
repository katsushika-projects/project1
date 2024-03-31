from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import get_user_model

from .views import JWTokenObtainView, JWTokenRefreshView, LogoutView, UserListAPIView, UserViewSet, UserDetailAPIView, UserBlockAPIView


router = DefaultRouter()
router.register("users", UserViewSet)
User = get_user_model()
urlpatterns = [
    path("auth/", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("users/", UserListAPIView.as_view()),
    path("users/<uuid:pk>/", UserDetailAPIView.as_view()),
    path("users/<uuid:pk>/block/", UserBlockAPIView.as_view()),
    path("auth/jwt/create/", JWTokenObtainView.as_view(), name="login"),
    path("auth/jwt/refresh/", JWTokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
]
