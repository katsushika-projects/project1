from django.urls import path

from .views import MessageCreateView, MessageListAPIView

urlpatterns = [
    path("create/", MessageCreateView.as_view(), name="message-create"),
    path("", MessageListAPIView.as_view(), name="message-list"),
]
