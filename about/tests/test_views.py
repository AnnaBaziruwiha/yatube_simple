from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        author_page_name = reverse(
            "about:author")
        tech_page_name = reverse(
            "about:tech")
        templates_pages_names = {
            "about/author.html": author_page_name,
            "about/tech.html": tech_page_name,
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
