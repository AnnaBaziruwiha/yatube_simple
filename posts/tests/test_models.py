from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="Тестовый пользователь",
            password="123"
        )
        cls.group = Group.objects.create(
            title="Лев Толстой",
            slug="leo",
            description="Цитаты Льва Толстого"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            group=cls.group,
            author=cls.user
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Запись",
            "group": "Группа",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Напишите что-нибудь здесь.",
            "group": "Выберите группу, или оставьте поле пустым."
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str_method(self):
        """результат вызова метода str совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        field_str = {
            post: post.text[:15],
            group: group.title
        }

        for value, expected in field_str.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(value), expected)
