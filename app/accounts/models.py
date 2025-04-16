import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("メールアドレスは必須です")

        email = self.normalize_email(email)
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    
    firebase_uid = models.CharField(
    max_length=128,
    unique=True,
    null=True,
    blank=True,
    verbose_name="Firebase UID",
    )

    id = models.UUIDField(
        verbose_name="ユーザーID",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        verbose_name="メールアドレス",
        max_length=350,
        unique=True,
    )
    
    username = models.CharField(
    max_length=150,
    unique=True,
    null=True,
    blank=True,
    verbose_name="ユーザー名"
    )

    is_staff = models.BooleanField(
        verbose_name="管理サイトアクセス権限フラグ",
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name="アカウント有効フラグ",
        default=False,
    )
    created_at = models.DateTimeField(
        verbose_name="作成日",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="更新日",
        auto_now=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"

    def __str__(self):
        return self.email


class Block(models.Model):
    id = models.UUIDField(
        verbose_name="ブロックID",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        verbose_name="ブロック元ユーザー",
        related_name="block_from",
        on_delete=models.CASCADE,
    )
    blocked_user = models.ForeignKey(
        User,
        verbose_name="ブロック先ユーザー",
        related_name="block_for",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        verbose_name="作成日",
        auto_now_add=True,
    )
    deleted_at = models.DateTimeField(
        verbose_name="削除日",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "ブロック"
        verbose_name_plural = "ブロック"

    def __str__(self):
        return f"{self.user.email} --> {self.blocked_user.email}"

    def create_exclude_user_id_list_by_request_user(request_user):
        user_list_blocked = list(Block.objects.filter(user=request_user).values_list("blocked_user", flat=True))
        user_list_blocked_by = list(Block.objects.filter(blocked_user=request_user).values_list("user", flat=True))
        return user_list_blocked + user_list_blocked_by
