# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User

from .models import Campus, University


class UniversityTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(name="テスト大学1")
        self.url_list = reverse("university-list")
        self.url_detail = reverse("university-detail", kwargs={"pk": self.university.id})

    def test_get_university_detail(self):
        """
        大学取得APIのテスト
        """
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_university_list(self):
        """
        大学一覧取得APIのテスト
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CampusTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(name="テスト大学１")
        self.campus = Campus.objects.create(university=self.university, campus="テストキャンパス1")
        self.campus_list = reverse("campus-list")
        self.campus_detail = reverse("campus-detail", kwargs={"pk": self.campus.id})
        self.user = User.objects.create_user(email="test@test.com", password="testpassword")
        self.user.is_active = True
        self.user.save()
        self.login_url = reverse("login")
        self.data = {"email": self.user.email, "password": "testpassword"}
        self.client.post(self.login_url, self.data, format="json")

    def test_get_campus(self):
        """
        キャンパス取得APIのテスト
        """
        response = self.client.get(self.campus_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_campuses_list(self):
        """
        キャンパス一覧取得APIのテスト
        """
        response = self.client.get(self.campus_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
