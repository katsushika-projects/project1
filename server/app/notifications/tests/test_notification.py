from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification

User = get_user_model()


class NotificationTest(APITestCase):
    fixtures = [
        "accounts/fixtures/users.yaml",
        "notifications/fixtures/notifications.yaml",
    ]

    def setUp(self):
        url = reverse("login")  # JWTトークン取得エンドポイント
        data = {"email": "test1@example.com", "password": "test"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]  # JWTアクセストークンを取得
        self.client.cookies["access_token"] = token

    def test_get_notification_list(self):
        """
        通知リストを取得するテスト
        """
        url = reverse("notifications:notification-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class UpdateNotificationImportanceTest(APITestCase):
    fixtures = [
        "accounts/fixtures/users.yaml",
        "notifications/fixtures/notifications.yaml",
    ]

    def setUp(self):
        url = reverse("login")  # JWTトークン取得エンドポイント
        data = {"email": "test1@example.com", "password": "test"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]  # JWTアクセストークンを取得
        self.client.cookies["access_token"] = token

    def test_update_notification_importance(self):
        """
        通知の重要度を更新するテスト True -> False
        """
        notification = Notification.objects.get(pk="7b6f8e41-23bf-49c6-8fbb-459118c4eb0e")
        self.assertEqual(notification.is_important, True)
        url = reverse(
            "notifications:notification-update-importance", kwargs={"pk": "7b6f8e41-23bf-49c6-8fbb-459118c4eb0e"}
        )
        data = {"is_important": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_important"], False)

    def test_update_notification_importance2(self):
        """
        通知の重要度を更新するテスト True -> True
        """
        notification = Notification.objects.get(pk="7b6f8e41-23bf-49c6-8fbb-459118c4eb0e")
        self.assertEqual(notification.is_important, True)
        url = reverse(
            "notifications:notification-update-importance", kwargs={"pk": "7b6f8e41-23bf-49c6-8fbb-459118c4eb0e"}
        )
        data = {"is_important": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_important"], True)

    def test_update_notification_importance_3(self):
        """
        通知の重要度を更新するテスト False -> True
        """
        notification = Notification.objects.get(pk="d37dbd2c-b2a2-4e19-a6d5-ba5480380e27")
        self.assertEqual(notification.is_important, False)
        url = reverse(
            "notifications:notification-update-importance", kwargs={"pk": "d37dbd2c-b2a2-4e19-a6d5-ba5480380e27"}
        )
        data = {"is_important": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_important"], True)

    def test_update_notification_importance_4(self):
        """
        通知の重要度を更新するテスト False -> False
        """
        notification = Notification.objects.get(pk="d37dbd2c-b2a2-4e19-a6d5-ba5480380e27")
        self.assertEqual(notification.is_important, False)
        url = reverse(
            "notifications:notification-update-importance", kwargs={"pk": "d37dbd2c-b2a2-4e19-a6d5-ba5480380e27"}
        )
        data = {"is_important": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_important"], False)
