# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import University


class UniversityTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(name="テスト大学1")
        self.url_list = reverse("university-list")
        self.url_detail = reverse("university-detail", kwargs={"pk": self.university.id})

    def test_get_university_list(self):
        """
        大学の一覧取得APIのテスト
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
