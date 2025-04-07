from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "item_id",
            "user",
            "user_email",
            "message",
            "created_at",
        )
        read_only_fields = [
            "id",
            "created_at",
            "user",
        ]

    def get_user_email(self, obj):
        return obj.user.email
