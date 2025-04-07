from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message as FCMMessage
from firebase_admin.messaging import Notification as FCMNotification
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification

from .models import Message
from .serializers import MessageSerializer


class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        self.create_notification(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def create_notification(self, serializer):
        title = "取引メッセージが届きました"
        message = f"{serializer.instance.message}"
        if serializer.instance.user != serializer.instance.item_id.seller:
            user = serializer.instance.item_id.seller
        else:
            user = serializer.instance.item_id.buyer
        # 通知保存
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
        )
        # FCM通知
        message = FCMMessage(
            notification=FCMNotification(title=title, body=message),
        )
        devices = FCMDevice.objects.filter(user=user)
        devices.send_message(message)


class MessageListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        messages = Message.objects.all()

        # item_idクエリパラメータが存在すればフィルタリング
        item_id = request.query_params.get("item_id", None)
        if item_id:
            messages = messages.filter(item_id=item_id)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
