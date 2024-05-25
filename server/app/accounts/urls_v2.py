from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views_v2 import (
    BlockedUserListAPIView,
    JWTokenObtainView,
    JWTokenRefreshView,
    LogoutView,
    UserBlockAPIView,
    UserDetailAPIView,
    UserListAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("auth/", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("users/", UserListAPIView.as_view()),
    path("users/<uuid:pk>/", UserDetailAPIView.as_view()),
    path("users/<uuid:pk>/block/", UserBlockAPIView.as_view()),
    path("blocked_user_list/", BlockedUserListAPIView.as_view()),
    path("auth/jwt/create/", JWTokenObtainView.as_view(), name="login"),
    path("auth/jwt/refresh/", JWTokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
]
