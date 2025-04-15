from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.middleware.csrf import get_token
from djoser import utils
from djoser import views as djoser_views
from rest_framework import permissions, status
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import exceptions, views
from rest_framework.permissions import AllowAny
from firebase_admin import auth as firebase_auth

from items.models import Item
from transaction_messages.models import Message

from .models import Block
from .serializers import UserSerializer

User = get_user_model()


class FirebaseLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "トークンが必要です"}, status=400)

        id_token = auth_header.split("Bearer ")[1]
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            firebase_email = decoded_token.get("email")
        except Exception as e:
            print(request.data)
            return Response({"detail": f"Firebase認証に失敗: {str(e)}"}, status=401)

        user, created = User.objects.get_or_create(
            email=firebase_email,
            defaults={"is_active": True},
        )

        return Response({
            "uid": user.id,
            "email": user.email,
            "new_user": created
        }, status=200)


def get_csrf_token(request):
    csrf_token = get_token(request)
    response = HttpResponse()
    response.set_cookie("csrftoken", csrf_token, httponly=True)
    return response


class UserViewSet(djoser_views.UserViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # 関連データの更新・削除のため、"削除済みユーザー"（ダミーユーザー）を用意
        if not User.objects.filter(email="deleted@example.com").exists():
            User.objects.create_user(email="deleted@example.com", password="deleted_user_password")
        deleted_user = User.objects.get(email="deleted@example.com")

        # 関連するItemの処理
        user_items = Item.objects.filter(Q(seller=instance) | Q(buyer=instance)).distinct()
        for user_item in user_items:
            # 取引中の商品があればアカウント削除は許可しない
            if user_item.listing_status == Item.ListingStatus.PURCHASED:
                raise ValidationError(
                    detail="取引中の商品があるため、アカウントを削除できません"
                )
            if user_item.seller == instance:
                # 出品者の場合は、その商品を削除
                user_item.delete()
            elif user_item.buyer == instance:
                # 購入者の場合は、ダミーユーザーに再割り当て
                user_item.buyer = deleted_user
                user_item.save()

        # 関連するMessageの処理：ユーザーをダミーユーザーに変更
        user_messages = Message.objects.filter(user=instance)
        for user_message in user_messages:
            user_message.user = deleted_user
            user_message.save()

        # Firebaseのユーザーも削除する
        try:
            # Firebase上のユーザー情報はメールアドレスで取得
            firebase_user = firebase_auth.get_user_by_email(instance.email)
            firebase_auth.delete_user(firebase_user.uid)
        except Exception as e:
            # Firebase側の削除に失敗した場合は、エラーを返して以降の削除処理を中断
            raise ValidationError(detail=f"Firebaseのユーザー削除に失敗: {str(e)}")

        # ログイン中のユーザーの場合、セッションからもログアウト
        if instance == request.user:
            utils.logout_user(self.request)

        # DB上からユーザーを削除
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        if not User.objects.filter(id=user_id).exists():
            raise ValidationError(detail="ユーザーが存在しません")
        instance = User.objects.get(id=user_id)
        serializer = UserSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlockedUserListAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        blocked_user_id_list = Block.objects.filter(user=self.request.user).values_list("blocked_user", flat=True)
        queryset = User.objects.filter(id__in=blocked_user_id_list)
        return queryset


class UserBlockAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        if not User.objects.filter(id=user_id).exists():
            raise ParseError(detail="ユーザーが存在しません")

        user = User.objects.get(id=user_id)
        if user == self.request.user:
            raise ParseError(detail="自分自身をブロックすることはできません")
        if Block.objects.filter(user=self.request.user, blocked_user=user).exists():
            raise ParseError(detail="既にブロックしています")
        if Item.objects.filter(
            seller=self.request.user, buyer=user, listing_status=Item.ListingStatus.PURCHASED
        ).exists():
            raise ParseError(detail="取引中のユーザーはブロックできません")
        if Item.objects.filter(
            seller=user, buyer=self.request.user, listing_status=Item.ListingStatus.PURCHASED
        ).exists():
            raise ParseError(detail="取引中のユーザーはブロックできません")

        Block.objects.create(user=self.request.user, blocked_user=user)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        if not User.objects.filter(id=user_id).exists():
            raise ParseError(detail="ユーザーが存在しません")
        instance = User.objects.get(id=user_id)
        if not Block.objects.filter(user=self.request.user, blocked_user=instance).exists():
            raise ParseError(detail="ブロックしていません")
        Block.objects.filter(user=self.request.user, blocked_user=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# from django.contrib.auth import get_user_model
# from django.db.models import Q
# from django.http import HttpResponse
# from django.middleware.csrf import get_token
# from djoser import utils
# from djoser import views as djoser_views
# from rest_framework import permissions, status
# from rest_framework.exceptions import ParseError, ValidationError
# from rest_framework.generics import ListAPIView
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt import exceptions, views
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from django.contrib.auth import get_user_model
# from firebase_admin import auth as firebase_auth

# from items.models import Item
# from transaction_messages.models import Message

# from .models import Block
# from .serializers import UserSerializer

# User = get_user_model()


# class FirebaseLoginView(APIView):
#     permission_classes = [AllowAny]  # ログイン前なので許可

#     def post(self, request):
#         auth_header = request.headers.get("Authorization")
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return Response({"detail": "トークンが必要です"}, status=400)

#         id_token = auth_header.split("Bearer ")[1]
#         try:
#             decoded_token = firebase_auth.verify_id_token(id_token)
#             firebase_email = decoded_token.get("email")
#         except Exception as e:
#             print(request.data)
#             return Response({"detail": f"Firebase認証に失敗: {str(e)}"}, status=401)

#         user, created = User.objects.get_or_create(
#             email=firebase_email,
#             defaults={"is_active": True},
#         )

#         # モバイルアプリ用：user IDだけ返すなど
#         return Response({
#             "uid": user.id,
#             "email": user.email,
#             "new_user": created
#         }, status=200)


# def get_csrf_token(request):
#     csrf_token = get_token(request)
#     response = HttpResponse()
#     # CSRFトークンをHTTPOnlyのクッキーにセット
#     response.set_cookie("csrftoken", csrf_token, httponly=True)
#     return response


# class UserViewSet(djoser_views.UserViewSet):
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)

#         user_items = Item.objects.filter(Q(seller=instance) | Q(buyer=instance)).distinct()
#         if not User.objects.filter(email="deleted@example.com").exists():
#             User.objects.create_user(email="deleted@example.com", password="deleted_user_password")
#         deleted_user = User.objects.get(email="deleted@example.com")
#         for user_item in user_items:
#             if user_item.listing_status == Item.ListingStatus.PURCHASED:
#                 raise ValidationError(
#                     detail="取引中の商品があるため、アカウントを削除できません",
#                 )
#             if user_item.seller == instance:
#                 user_item.delete()
#             elif user_item.buyer == instance:
#                 user_item.buyer = deleted_user
#             user_item.save()

#         user_messages = Message.objects.filter(user=instance)
#         for user_message in user_messages:
#             user_message.user = deleted_user
#             user_message.save()

#         if instance == request.user:
#             utils.logout_user(self.request)
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class UserDetailAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         user_id = kwargs.get("pk")
#         if not User.objects.filter(id=user_id).exists():
#             raise ValidationError(detail="ユーザーが存在しません")
#         instance = User.objects.get(id=user_id)
#         serializer = UserSerializer(instance)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class BlockedUserListAPIView(ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = UserSerializer

#     def get_queryset(self):
#         blocked_user_id_list = Block.objects.filter(user=self.request.user).values_list("blocked_user", flat=True)
#         queryset = User.objects.filter(id__in=blocked_user_id_list)
#         return queryset


# class UserBlockAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         user_id = kwargs.get("pk")
#         if not User.objects.filter(id=user_id).exists():
#             raise ParseError(detail="ユーザーが存在しません")

#         user = User.objects.get(id=user_id)
#         if user == self.request.user:
#             raise ParseError(detail="自分自身をブロックすることはできません")
#         if Block.objects.filter(user=self.request.user, blocked_user=user).exists():
#             raise ParseError(detail="既にブロックしています")
#         if Item.objects.filter(
#             seller=self.request.user, buyer=user, listing_status=Item.ListingStatus.PURCHASED
#         ).exists():
#             raise ParseError(detail="取引中のユーザーはブロックできません")
#         if Item.objects.filter(
#             seller=user, buyer=self.request.user, listing_status=Item.ListingStatus.PURCHASED
#         ).exists():
#             raise ParseError(detail="取引中のユーザーはブロックできません")

#         Block.objects.create(user=self.request.user, blocked_user=user)
#         return Response(status=status.HTTP_201_CREATED)

#     def delete(self, request, *args, **kwargs):
#         user_id = kwargs.get("pk")
#         if not User.objects.filter(id=user_id).exists():
#             raise ParseError(detail="ユーザーが存在しません")
#         instance = User.objects.get(id=user_id)
#         if not Block.objects.filter(user=self.request.user, blocked_user=instance).exists():
#             raise ParseError(detail="ブロックしていません")
#         Block.objects.filter(user=self.request.user, blocked_user=instance).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
