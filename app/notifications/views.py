from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer, UpdateNotificationImportanceSerializer


class NotificationView(APIView):
    """
    Notification API View
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all notifications
        """
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateNotificationImportanceView(APIView):
    """
    Update Notification API View
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Update notification
        """
        notification_id = self.kwargs["pk"]
        notification = get_object_or_404(Notification, pk=notification_id)
        if notification.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UpdateNotificationImportanceSerializer(notification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
