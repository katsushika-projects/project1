from django.urls import path

from .views import NotificationView, UpdateNotificationImportanceView

app_name = "notifications"

urlpatterns = [
    path("", NotificationView.as_view(), name="notification-list"),
    path(
        "<uuid:pk>/update-importance/",
        UpdateNotificationImportanceView.as_view(),
        name="notification-update-importance",
    ),
]
