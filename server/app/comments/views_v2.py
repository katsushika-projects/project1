from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message as FCMMessage
from firebase_admin.messaging import Notification as FCMNotification
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Block
from notifications.models import Notification

from .models import Comment
from .serializers_v2 import CommentSerializer

User = get_user_model()


class CommentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request_user": self.request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        self.create_notification(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def create_notification(self, serializer):
        # 販売者とコメントしたユーザーに通知を送る(自分は除外する)
        users = []
        users.append(serializer.instance.item_id.seller)
        comment_user = User.objects.filter(comment__item_id=serializer.instance.item_id).distinct()
        users.extend(comment_user)
        users = [user for user in users if user != serializer.instance.user]

        title = "コメントが投稿されました"
        message = f"{serializer.instance.item_id.name} にコメントが投稿されました。"

        # 通知保存

        for user in users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
            )
            # FCM通知対象のデバイスにトピック設定
            FCMDevice.objects.filter(user=user).handle_topic_subscription(True, topic="comment")

        # FCM通知
        message = FCMMessage(
            notification=FCMNotification(title=title, body=message),
        )
        FCMDevice.send_topic_message(message, "comment")
        FCMDevice.objects.all().handle_topic_subscription(False, topic="comment")


class CommentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        comments = Comment.objects.all()

        # item_idクエリパラメータが存在すればフィルタリング
        item_id = request.query_params.get("item_id", None)
        if item_id:
            comments = comments.filter(item_id=item_id)

        exclude_user_list = Block.create_exclude_user_id_list_by_request_user(request.user)
        comments = comments.exclude(user__in=exclude_user_list)

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
