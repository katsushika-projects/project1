from django.urls import path

from .views_v2 import NotificationView, UpdateNotificationImportanceView

app_name = "notifications_v2"

urlpatterns = [
    path("", NotificationView.as_view(), name="notification-list"),
    path(
        "<uuid:pk>/update-importance/",
        UpdateNotificationImportanceView.as_view(),
        name="notification-update-importance",
    ),
]
