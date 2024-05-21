from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Block

User = get_user_model()


class RefreshTokenTest(APITestCase):
    fixtures = ["accounts/tests/fixtures/accounts/user.yaml"]

    def setUp(self):
        self.user = User.objects.get(id="00000000-0000-0000-0000-000000000001")

    def test_refresh_token(self):
        """id: acc-000001"""
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies.load({"refresh_token": str(refresh), "access_token": str(refresh.access_token)})
        response = self.client.post(
            "/api/auth/jwt/refresh/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BlockTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="blocked@blocked.com", password="blockedpassword")
        self.request_user = User.objects.create_user(email="block@block.com", password="blockpassword")
        self.block_user_url = reverse("block-user", kwargs={"pk": self.user.id})
        self.block_list_url = reverse("block-list")
        self.request_user.is_active = True
        self.request_user.save()
        self.login_url = reverse("login")
        self.data = {"email": self.request_user.email, "password": "blockpassword"}
        self.client.post(self.login_url, self.data, format="json")

    def test_post_block_user(self):
        response = self.client.post(self.block_user_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_block_user(self):
        self.block = Block.objects.create(user=self.request_user, blocked_user=self.user)
        response = self.client.delete(self.block_user_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_block_list(self):
        response = self.client.get(self.block_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
