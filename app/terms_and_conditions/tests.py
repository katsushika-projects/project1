from django.test import TestCase
from django.urls import reverse


class StaticPagesTests(TestCase):
    def test_terms_of_service_page(self):
        """
        このテストは、利用規約ページが正常にレンダリングされることを確認します。
        """
        response = self.client.get(reverse("terms_of_service"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "terms_and_conditions/terms_of_service.html")

    def test_privacy_policy_page(self):
        """
        このテストは、プライバシーポリシーページが正常にレンダリングされることを確認します。
        """
        response = self.client.get(reverse("privacy_policy"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "terms_and_conditions/privacy_policy.html")
