from django.test import Client, TestCase


class AboutUrlTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        """Страница /about/author/ доступна любому пользователю"""
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        """Страница /about/tech/ доступна любому пользователю"""
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, 200)
