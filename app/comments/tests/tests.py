from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from items.models import Item
from notifications.models import Notification

User = get_user_model()


class CommentCreateTest(TestCase):
    fixtures = [
        "comments/tests/fixtures/users.yaml",
        "comments/tests/fixtures/universities.yaml",
        "comments/tests/fixtures/campuses.yaml",
        "comments/tests/fixtures/items.yaml",
        "comments/tests/fixtures/comments.yaml",
    ]

    """
    コメント作成機能のテストクラス。

    属性:
    - client: APIリクエストを行うためのAPIClientのインスタンス。
    - user: テストのために作成されたテストユーザー。
    - item: テストのために作成されたサンプルアイテム。
    - comment_data: テストで使用されるサンプルのコメントデータ。
    - url: コメント作成のためのAPIエンドポイントのURL。
    """

    def setUp(self):
        """
        テストケースのセットアップメソッド。テストユーザーとアイテムを作成し、それで認証します。
        また、APIエンドポイントのURLとサンプルのコメントデータを設定します。
        """
        self.client = APIClient()
        # self.user: test1
        self.user = User.objects.get(pk="5f1c7d7d-52ce-422f-8c4b-4e9e5d92db5d")
        self.client.force_authenticate(user=self.user)
        # self.item: seller=test1, buyer=null
        self.item = Item.objects.get(pk="c1c61f36-6032-4d39-a649-6ad16ee4f00c")
        self.comment_data = {"message": "テストコメント", "item_id": self.item.id}
        self.url = reverse("comment-create")

    def test_create_comment(self):
        """
        アイテムIDを指定して、コメントの作成APIエンドポイントにPOSTリクエストを行い、
        コメントが正常にアイテムに関連付けて作成されることを確認するテストメソッド。
        """
        response = self.client.post(self.url, self.comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], self.comment_data["message"])
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["item_id"], self.item.id)

    def test_count_notifications(self):
        """自分の商品にコメントした場合"""
        pre_notification_count = Notification.objects.count()
        response = self.client.post(self.url, self.comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), pre_notification_count)

    def test_count_notifications2(self):
        """
        1つの他人のコメントがついている自分の商品にコメント
        → 通知はコメントしている他人用が1つ増える
        """
        comment_data = {"message": "テストコメント", "item_id": "c1c61f36-6032-4d39-a649-6ad16ee4f01c"}
        pre_notification_count = Notification.objects.count()
        response = self.client.post(self.url, comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), pre_notification_count + 1)

    def test_count_notifications3(self):
        """
        Aさんの商品にBさんがコメントしているとき，
        CさんがAさんの商品にコメントしたとき．
        → 通知はAさんとBさん用で2つ増える
        Aさん: test1
        Bさん: test2
        Cさん: test3
        """

        user = User.objects.get(pk="eadcfad7-69df-4f8a-bac3-61bc4466d4b5")
        self.client.force_authenticate(user=user)
        comment_data = {"message": "テストコメント", "item_id": "c1c61f36-6032-4d39-a649-6ad16ee4f01c"}
        pre_notification_count = Notification.objects.count()
        response = self.client.post(self.url, comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), pre_notification_count + 2)
