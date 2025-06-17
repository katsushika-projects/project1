from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("campuses.urls")),
    path("api/v2/", include("campuses.urls")),
    path("api/comment/", include("comments.urls")),
    path("api/v2/comment/", include("comments.urls_v2")),
    path("api/items/", include("items.urls")),
    path("api/v2/items/", include("items.urls_v2")),
    path("api/notification/", include("notifications.urls", namespace="notifications")),
    path("api/v2/notification/", include("notifications.urls_v2", namespace="notifications_v2")),
    path("api/messages/", include("transaction_messages.urls")),
    path("api/v2/messages/", include("transaction_messages.urls")),
    path("api/", include("accounts.urls")),
    path("api/v2/", include("accounts.urls_v2")),
    path("", include("terms_and_conditions.urls")),
    path("api/devices/", FCMDeviceAuthorizedViewSet.as_view({"post": "create"}), name="create_fcm_device"),
    path("api/v2/devices/", FCMDeviceAuthorizedViewSet.as_view({"post": "create"}), name="create_fcm_device"),
    path("api/", include("ping.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
