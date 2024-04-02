from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("campuses.urls")),
    path("api/comment/", include("comments.urls")),
    path("api/items/", include("items.urls")),
    path("api/notification/", include("notifications.urls")),
    path("api/messages/", include("transaction_messages.urls")),
    path("api/", include("accounts.urls")),
    path("", include("terms_and_conditions.urls")),
    path("api/devices/", FCMDeviceAuthorizedViewSet.as_view({"post": "create"}), name="create_fcm_device"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
