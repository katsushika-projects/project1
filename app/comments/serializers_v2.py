from rest_framework import serializers

from accounts.models import Block
from items.models import Item

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    message = serializers.CharField(source="comment")

    class Meta:
        model = Comment
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

    def get_message(self, obj):
        return obj.comment

    def validate_item_id(self, value):
        request_user = self.context.get("request_user")
        exclude_user_id_list = Block.create_exclude_user_id_list_by_request_user(request_user)
        item = Item.objects.filter(id=value.id).select_related("seller").first()
        # if not item:
        #     raise serializers.ValidationError("商品が存在しません")
        if item.listing_status != Item.ListingStatus.UNPURCHASED:
            raise serializers.ValidationError("未購入の商品にのみコメントできます")
        if item.seller.id in exclude_user_id_list:
            raise serializers.ValidationError("ブロック中/被ブロック中のユーザーの商品にはコメントできません")
        return value
