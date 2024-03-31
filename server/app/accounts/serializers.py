from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(UserCreatePasswordRetypeSerializer):
    email = serializers.EmailField(
        validators=[RegexValidator(regex=r"\d{7}@ed.tus.ac.jp", message="メールアドレスの形式は 7桁の学籍番号@ed.tus.ac.jp です")],
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class UserDeleteSerializer(serializers.Serializer):
    pass
