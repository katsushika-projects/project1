from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from items.models import Item

User = get_user_model()


class CommentCreateTest(TestCase):
    fixtures = [
        "accounts/fixtures/data.json",
        "campuses/fixtures/data.json",
        "items/fixtures/data.json",
    ]

    """
    メッセージ作成機能のテストクラス。

    属性:
    - client: APIリクエストを行うためのAPIClientのインスタンス。
    - user: テストのために作成されたテストユーザー。
    - item: テストのために作成されたサンプルアイテム。
    - comment_data: テストで使用されるサンプルのコメントデータ。
    - url: メッセージ作成のためのAPIエンドポイントのURL。
    """

    def setUp(self):
        """
        テストケースのセットアップメソッド。テストユーザーとアイテムを作成し、それで認証します。
        また、APIエンドポイントのURLとサンプルのメッセージデータを設定します。
        """
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpass")
        self.item = Item.objects.get(pk="6fd2f1142af84d4586586d64324be72d")
        self.client.force_authenticate(user=self.user)
        self.message_data = {"message": "テストメッセージ", "item_id": self.item.id}
        self.url = reverse("message-create")

    def test_create_message(self):
        """
        アイテムIDを指定して、メッセージの作成APIエンドポイントにPOSTリクエストを行い、
        メッセージが正常にアイテムに関連付けて作成されることを確認するテストメソッド。
        """
        response = self.client.post(self.url, self.message_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], self.message_data["message"])
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["item_id"], self.item.id)
