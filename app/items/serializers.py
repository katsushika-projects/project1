from rest_framework import serializers

from .models import Image, Item, Report

# from PIL import Image as PILImage
# import io


class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("photo_path", "order")


class ItemSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source="seller.email", default=serializers.CurrentUserDefault())
    seller_id = serializers.ReadOnlyField(source="seller.id")
    receivable_campus = serializers.CharField(source="receivable_campus.campus")
    images = ItemImageSerializer(many=True)
    is_liked_by_current_user = serializers.SerializerMethodField()

    def get_buyer(self, obj):
        if obj.buyer:
            return obj.buyer.email
        return None

    def get_buyer_id(self, obj):
        if obj.buyer:
            return obj.buyer.id
        return None

    def get_is_liked_by_current_user(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.liked_by.filter(user=user).exists()
        return False

    class Meta:
        model = Item
        fields = "__all__"


class ItemCreateSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, write_only=True)  # write_only を追加

    class Meta:
        model = Item
        fields = (
            "images",
            "id",
            "seller",
            "buyer",
            "listing_status",
            "price",
            "name",
            "description",
            "condition",
            "writing_state",
            "receivable_campus",
        )

    def create(self, validated_data):
        images_data = validated_data.pop("images")
        item = Item.objects.create(**validated_data)
        for image_data in images_data:
            Image.objects.create(parent_item=item, **image_data)
        return item

    def update(self, instance, validated_data):
        print("validated_data: ", validated_data)
        images_data = validated_data.pop("images")
        item = super().update(instance, validated_data)
        self.update_images(item, images_data)
        return instance

    def update_images(self, item, images_data):
        # 画像の更新
        # partial=Trueのとき
        if self.partial:
            for image in images_data:
                # 元の画像画像を削除 (存在するなら)
                ex_image = item.images.filter(order=image["order"])
                ex_image.delete()
                Image.objects.update_or_create(parent_item=item, **image)
        # partial=Falseのとき
        else:
            existing_images = item.images.all()
            existing_images.delete()
            for image in images_data:
                Image.objects.update_or_create(parent_item=item, **image)


class ItemReportSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ItemReportSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Report
        fields = ["reason"]
        read_only_fields = ["id", "created_at", "reporter_id", "item_id"]
