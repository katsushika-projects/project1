from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class UpdateNotificationImportanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["is_important"]
