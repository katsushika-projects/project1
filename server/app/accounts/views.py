from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt import exceptions, views
from djoser import views as djoser_views
from djoser import utils

from items.models import Item
from transaction_messages.models import Message
from .authentication import CookieJWTAuthentication
from .serializers import UserSerializer

User = get_user_model()


class UserListAPIView(ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer


# 　JWTをcookieに持たせる
class JWTokenObtainView(views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.TokenError as e:
            raise exceptions.InvalidToken(e.args[0])

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        # Cookieにトークンをセット
        response.set_cookie(
            "access_token",
            serializer.validated_data["access"],
            # 期限は3時間
            max_age=60 * 60 * 3,
            httponly=True,
        )
        response.set_cookie(
            "refresh_token",
            serializer.validated_data["refresh"],
            # 期限は1週間
            max_age=60 * 60 * 24 * 7,
            httponly=True,
        )

        return response


# JWTのリフレッシュ
class JWTokenRefreshView(views.TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # cookieからリフレッシュトークンを取得
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "No refresh"}, status=status.HTTP_400_BAD_REQUEST)

        # リクエストにリフレッシュトークンを含めなおす
        request_data = request.data.copy()
        request_data["refresh"] = refresh_token
        serializer = self.get_serializer(data=request_data)

        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.TokenError as e:
            raise exceptions.InvalidToken(e.args[0])

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        response.set_cookie(
            "access_token",
            serializer.validated_data["access"],
            max_age=60 * 60 * 3,
            httponly=True,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=60 * 60 * 24 * 7,
            httponly=True,
        )

        return response


class LogoutView(views.TokenBlacklistView):
    authentication_classes = (CookieJWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "No refresh"}, status=status.HTTP_400_BAD_REQUEST)

        # リクエストにリフレッシュトークンを含めなおす
        request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        # トークンをCookieから削除
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        # 既に存在するresponseにdataを追加
        response.data = {"Message": "Logout"}

        return response


def get_csrf_token(request):
    csrf_token = get_token(request)
    response = HttpResponse()
    # CSRFトークンをHTTPOnlyのクッキーにセット
    response.set_cookie("csrftoken", csrf_token, httponly=True)
    return response


class UserViewSet(djoser_views.UserViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        user_items = Item.objects.filter(Q(seller=instance) | Q(buyer=instance)).distinct()
        if not User.objects.filter(email="deleted@example.com").exists():
            User.objects.create_user(email="deleted@example.com", password="deleted_user_password")
        deleted_user = User.objects.get(email="deleted@example.com")
        for user_item in user_items:
            if user_item.listing_status == Item.ListingStatus.PURCHASED:
                raise ValidationError(
                    detail = "取引中の商品があるため、アカウントを削除できません",
                )
            if user_item.seller == instance:
                user_item.delete()
            elif user_item.buyer == instance:
                user_item.buyer = deleted_user
            user_item.save()

        user_messages = Message.objects.filter(user=instance)
        for user_message in user_messages:
            user_message.user = deleted_user
            user_message.save()

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
