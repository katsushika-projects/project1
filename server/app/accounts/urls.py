from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BlockedUserListAPIView,
    UserBlockAPIView,
    UserDetailAPIView,
    UserListAPIView,
    UserViewSet,
)


router = DefaultRouter()
router.register("users", UserViewSet)
User = get_user_model()
urlpatterns = [
    path("auth/", include(router.urls)),
    path("users/", UserListAPIView.as_view()),
    path("users/<uuid:pk>/", UserDetailAPIView.as_view()),
    path("users/<uuid:pk>/block/", UserBlockAPIView.as_view()),
    path("blocked_user_list/", BlockedUserListAPIView.as_view()),
]
