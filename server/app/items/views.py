from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message as FCMMessage
from firebase_admin.messaging import Notification as FCMNotification
from rest_framework import generics, status, views
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification

from .models import Item, Like, Report
from .serializers import ItemCreateSerializer, ItemReportSerializer, ItemSerializer


class ItemListPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class ItemListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Item.objects.all().order_by("-updated_at")
    serializer_class = ItemSerializer
    pagination_class = ItemListPagination

    def get_queryset(self):
        queryset = self.queryset
        listing_status_list = [
            Item.ListingStatus.UNPURCHASED,
            Item.ListingStatus.PURCHASED,
            Item.ListingStatus.COMPLETED,
        ]
        queryset = queryset.filter(listing_status__in=listing_status_list)
        # 商品名で検索
        name_query = self.request.query_params.get("name", None)
        if name_query:
            queryset = queryset.filter(name__icontains=name_query)
        # 購入済みの商品を除外
        purchased_query = self.request.query_params.get("purchased", None)
        if purchased_query == "false":
            queryset = queryset.filter(listing_status=Item.ListingStatus.UNPURCHASED)
        return queryset


class ItemCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # request.dataを変更可能な辞書にコピー
        data = dict(request.data.lists())
        # Itemの作成に必要なキー
        keys_to_check = [
            "price",
            "name",
            "description",
            "condition",
            "writing_state",
            "receivable_campus",
        ]
        # キーが辞書に存在しないときエラーを返す
        for key in keys_to_check:
            if key not in data:
                return Response({"error": f"{key} が必要です"}, status=status.HTTP_400_BAD_REQUEST)

        data["seller"] = request.user.id
        data["listing_status"] = Item.ListingStatus.UNPURCHASED
        data["price"] = data["price"][0]
        data["name"] = data["name"][0]
        data["description"] = data["description"][0]
        data["condition"] = data["condition"][0]
        data["writing_state"] = data["writing_state"][0]
        data["receivable_campus"] = data["receivable_campus"][0]

        if "image_1" not in data:
            return Response({"error": "写真が必須です。"}, status=status.HTTP_400_BAD_REQUEST)
        data["images"] = []
        data["images"].append({"photo_path": data.pop("image_1")[0], "order": 1})
        # 10枚まで登録できるようにする
        for i in range(2, 11):
            if f"image_{i}" in data:
                data["images"].append({"photo_path": data.pop(f"image_{i}")[0], "order": i})
            else:
                break

        serializer = ItemCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            saved_item = Item.objects.get(id=serializer.data["id"])
            response_serializer = ItemSerializer(saved_item, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = self.request.query_params.get("partial", False)
        instance = self.get_object()
        print("partial: ", partial)
        print("keywargs: ", kwargs)

        if instance.listing_status == Item.ListingStatus.PURCHASED:
            return Response({"error": "購入された商品は編集できません。"}, status=status.HTTP_400_BAD_REQUEST)
        if instance.listing_status == Item.ListingStatus.COMPLETED:
            return Response({"error": "売り切れた商品は編集できません。"}, status=status.HTTP_400_BAD_REQUEST)

        # request.dataを変更可能な辞書にコピー
        data = dict(request.data.lists())
        # Itemの作成に必要なキー
        keys_to_check = [
            "price",
            "name",
            "description",
            "condition",
            "writing_state",
            "receivable_campus",
        ]
        # キーが辞書に存在しないときエラーを返す
        for key in keys_to_check:
            if key not in data:
                if partial:
                    continue
                else:
                    return Response({"error": f"{key} が必要です"}, status=status.HTTP_400_BAD_REQUEST)
            data[key] = data[key][0]

        data["seller"] = request.user.id
        data["listing_status"] = instance.listing_status

        # 以下画像の処理
        data["images"] = []
        # partial == True のとき
        if partial:
            for i in range(1, 11):
                if f"image_{i}" in data:
                    data["images"].append({"photo_path": data.pop(f"image_{i}")[0], "order": i})

        # partial == False のとき
        else:
            if "image_1" not in data:
                return Response({"error": "写真が必須です。"}, status=status.HTTP_400_BAD_REQUEST)
            data["images"] = []
            data["images"].append({"photo_path": data.pop("image_1")[0], "order": 1})
            # 10枚まで登録できるようにする
            for i in range(2, 11):
                if f"image_{i}" in data:
                    data["images"].append({"photo_path": data.pop(f"image_{i}")[0], "order": i})
                else:
                    break

        serializer = ItemCreateSerializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        updated_item = self.get_object()
        response_serializer = ItemSerializer(updated_item, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ItemPurchaseView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def update(self, request, *args, **kwargs):
        item = self.get_object()

        if item.seller == request.user:
            return Response({"error": "自分自身の商品を購入することはできません。"}, status=status.HTTP_400_BAD_REQUEST)

        item.buyer = request.user
        item.listing_status = Item.ListingStatus.PURCHASED
        item.save()

        # 通知関連
        user = item.seller
        title = "商品が購入されました"
        message = f"{item.name} が購入されました。"
        # 通知保存
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
        )
        # FMC通知
        message = FCMMessage(
            notification=FCMNotification(title=title, body=message),
        )
        devices = FCMDevice.objects.filter(user=user)
        devices.send_message(message)

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemCancelView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        item = self.get_object()

        if item.buyer is not None:
            return Response({"error": "購入された商品はキャンセルできません。"}, status=status.HTTP_400_BAD_REQUEST)
        if item.seller != request.user:
            return Response({"error": "あなたの出品物ではありません。"}, status=status.HTTP_400_BAD_REQUEST)
        item.listing_status = Item.ListingStatus.CANCELED
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data)


class ItemReListingView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        item = self.get_object()

        if item.seller != request.user:
            return Response({"error": "あなたの出品物ではありません。"}, status=status.HTTP_400_BAD_REQUEST)
        if item.listing_status != Item.ListingStatus.CANCELED:
            return Response({"error": "キャンセルされた商品以外は再出品できません。"}, status=status.HTTP_400_BAD_REQUEST)
        item.listing_status = Item.ListingStatus.UNPURCHASED
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data)


class ItemCompleteView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def update(self, request, *args, **kwargs):
        item = self.get_object()

        if item.buyer != request.user:
            return Response({"error": "購入者以外は購入完了できません。"}, status=status.HTTP_400_BAD_REQUEST)

        item.listing_status = Item.ListingStatus.COMPLETED
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data)


class ItemLikeToggleView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        item_id = kwargs["pk"]
        user_id = request.user.id

        if not Item.objects.filter(id=item_id).exists():
            return Response({"error": "商品が存在しません。"}, status=status.HTTP_400_BAD_REQUEST)

        if Like.objects.filter(item_id=item_id, user_id=user_id).exists():
            Like.objects.filter(item_id=item_id, user_id=user_id).delete()
            return Response({"message": "いいねを取り消しました。"})
        else:
            Like.objects.create(item_id=item_id, user_id=user_id)
            return Response({"message": "いいねしました。"})


class UserLikeItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemListPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Item.objects.filter(liked_by__user=user).prefetch_related("liked_by")
        listing_status_list = [Item.ListingStatus.UNPURCHASED, Item.ListingStatus.PURCHASED]
        queryset = queryset.filter(listing_status__in=listing_status_list)
        return queryset


class UserSellItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemListPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        sell_items = Item.objects.filter(seller=user).select_related("seller")
        return sell_items


class UserBuyItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemListPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        buy_items = Item.objects.filter(buyer=user).select_related("buyer")
        return buy_items


class ReportAPIView(APIView):
    def post(self, request, *args, **kwargs):
        item_id = kwargs["pk"]
        item = Item.objects.get(id=item_id)
        reporter = self.request.user
        if not item:
            raise ValidationError(detail="商品が存在しません。")
        if Report.objects.filter(item_id=item, reporter_id=reporter).exists():
            raise ValidationError(detail="既に報告済みです。")
        serializer = ItemReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(item_id=item, reporter_id=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
