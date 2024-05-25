from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from fcm_django.models import FCMDevice
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class DeviceRegistrationTest(TestCase):
    fixtures = [
        "config/tests/fixtures/users.yaml",
        "config/tests/fixtures/fcmdevices.yaml",
    ]

    def setUp(self):
        self.client = APIClient()
        self.device_registration_url = reverse("create_fcm_device")  # URL名を適切に設定
        self.device_data = {"registration_id": "test_registration_id", "type": "android"}
        self.user = User.objects.get(pk="5f1c7d7d-52ce-422f-8c4b-4e9e5d92db5d")
        self.client.force_authenticate(user=self.user)

    def test_device_registration(self):
        """
        デバイスを登録できるかテスト
        """
        pre_device_count = FCMDevice.objects.count()
        response = self.client.post(self.device_registration_url, self.device_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FCMDevice.objects.count(), pre_device_count + 1)
        self.assertEqual(FCMDevice.objects.last().registration_id, self.device_data["registration_id"])

    def test_device_registration_with_invalid_registration_id(self):
        """
        デバイス登録時に不正なデータを送信したときのテスト
        """
        pre_device_count = FCMDevice.objects.count()
        invalid_data = {"registration_id": "", "type": "android"}
        response = self.client.post(self.device_registration_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FCMDevice.objects.count(), pre_device_count)

    def test_device_registration_with_invalid_type(self):
        """
        デバイス登録時に不正なデータを送信したときのテスト
        """
        pre_device_count = FCMDevice.objects.count()
        invalid_data = {"registration_id": "", "type": "xox"}
        response = self.client.post(self.device_registration_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FCMDevice.objects.count(), pre_device_count)

    def test_device_registration_with_same_id(self):
        """
        他のユーザーのデバイスIDと同じデバイスIDが他ユーザーから登録されたとき
        """
        device = FCMDevice.objects.get(pk="1")
        device_data_duplicate_id = {"registration_id": device.registration_id, "type": "ios"}
        pre_device_count = FCMDevice.objects.count()
        self.assertNotEqual(device.user, self.user)  # 最初は他人に紐ずく
        response = self.client.post(self.device_registration_url, device_data_duplicate_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FCMDevice.objects.count(), pre_device_count)
        device.refresh_from_db()
        self.assertEqual(device.user, self.user)  # 今度は自分に紐ずく
