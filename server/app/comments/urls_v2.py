from django.urls import path

from .views_v2 import CommentCreateView, CommentListAPIView

urlpatterns = [
    path("create/", CommentCreateView.as_view(), name="comment-create"),
    path("", CommentListAPIView.as_view(), name="comment-list"),
]
