from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

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
