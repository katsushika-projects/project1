from django.urls import path

from .views import CommentCreateView, CommentListAPIView

urlpatterns = [
    path("create/", CommentCreateView.as_view(), name="comment-create"),
    path("", CommentListAPIView.as_view(), name="comment-list"),
]
