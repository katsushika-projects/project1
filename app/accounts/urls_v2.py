from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views_v2 import (
    UserBlockAPIView,
    UserDetailAPIView,
    UserViewSet,
    FirebaseLoginView
)

router = DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("auth/", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("users/<uuid:pk>/", UserDetailAPIView.as_view()),
    path("users/<uuid:pk>/block/", UserBlockAPIView.as_view()),
    path("auth/login/", FirebaseLoginView.as_view()),
]
