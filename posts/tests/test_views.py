import shutil

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

TEST_DIR = "test_data"


class PostPagesTests(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=(TEST_DIR + "/media"))
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username="test_author",
            first_name="Тестовый",
            last_name="автор"
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00"
            b"\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            group=Group.objects.create(
                title="Тестовая группа",
                slug="test_view_group",
                description="Группа для теста"
            ),
            author=cls.author,
            image=uploaded,
        )
        cls.group = Group.objects.create(
            title="Пустая группа",
            slug="empty",
            description="Пустая группа для проверки"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        print("\nDeleting temporary files...\n")
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="test_user")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = PostPagesTests.author
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group_slug = PostPagesTests.post.group.slug
        templates_pages_names = {
            "posts/index.html": reverse("index"),
            "posts/new.html": reverse("new_post"),
            "posts/group.html": (
                reverse("group_posts", kwargs={"slug": group_slug})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = self.authorized_client.get(reverse("index"))
        first_post = response.context["page"][0]
        expected_context = {
            post.text: first_post.text,
            post.author.get_full_name(): first_post.author.get_full_name(),
            post.image: first_post.image,
        }
        for expected, context in expected_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_group_page_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        post = PostPagesTests.post
        group_slug = post.group.slug
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": group_slug}))
        context_group = response.context["group"]
        context_post = response.context["page"][0]
        expected_context = {
            post.group.title: context_group.title,
            post.group.description: context_group.description,
            post.text: context_post.text,
            post.author.get_full_name(): context_post.author.get_full_name(),
            post.image: context_post.image,
        }
        for expected, context in expected_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_new_page_context(self):
        """Шаблон new для new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "group": forms.ModelChoiceField,
            "text": forms.CharField,
            "image": forms.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_post_in_right_group(self):
        """Пост группы не попал в неправильную группу
        Пустая группа осталась пустой
        """
        group_slug = PostPagesTests.group.slug
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": group_slug}))
        paginator = response.context["page"].paginator
        self.assertEqual(paginator.count, 0)

    def test_post_edit_page_context(self):
        """Шаблон new для post_edit сформирован с правильным контекстом."""
        post = PostPagesTests.post
        username = post.author.username
        response = self.author_client.get(reverse("post_edit", kwargs={
            "username": username,
            "post_id": post.pk,
        }))
        form_fields = {
            "group": forms.ModelChoiceField,
            "text": forms.CharField,
            "image": forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostPagesTests.post
        author = post.author
        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": author.username}))
        posts_count = Post.objects.filter(author=author).count()
        template_context = {
            author.get_full_name(): response.context["author"].get_full_name(),
            posts_count: response.context["posts"].count(),
            post.text: response.context["page"][0].text,
            post.image: response.context["page"][0].image,
        }
        for template, context in template_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, template)

    def test_post_page_context(self):
        """Шаблон post_view сформирован с правильным контекстом."""
        post = PostPagesTests.post
        author = post.author
        posts_count = Post.objects.filter(author=author).count()
        response = self.authorized_client.get(
            reverse("post", kwargs={"username": author.username,
                                    "post_id": post.pk}))
        response_post = response.context["post"]
        expected_context = {
            author.get_full_name(): response_post.author.get_full_name(),
            posts_count: response.context["posts"].count(),
            post.text: response_post.text,
            post.image: response_post.image,
        }
        for expected, context in expected_context.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_paginator_for_index_page(self):
        """В контекст главной страницы передается 10 постов"""
        self.group = PostPagesTests.group
        self.author = User.objects.create(username="author")
        for i in range(15):
            Post.objects.create(
                text="Тестовый текст",
                group=self.group,
                author=self.author,
            )
        response = self.authorized_client.get(reverse("index"))
        self.assertEqual(response.context["page"].start_index(), 1)
        self.assertEqual(response.context["page"].end_index(), 10)

    def test_index_page_cache(self):
        """Содержание страницы index сохраняется в кэше"""
        response = self.authorized_client.get(reverse("index"))
        Post.objects.create(
            text="Тест кэша",
            group=self.group,
            author=self.author,
        )
        response_cache = self.authorized_client.get(reverse("index"))
        self.assertIsNotNone(Post.objects.get(text="Тест кэша"))
        self.assertEqual(response.content, response_cache.content)

    def test_follow_authorized_user(self):
        """Авторизированный пользователь может подписываться на других
        пользователей
        """
        author = PostPagesTests.author
        self.authorized_client.get(reverse(
            "profile_follow",
            kwargs={"username": author.username}
        ))
        self.assertTrue(Follow.objects.filter(author=author,
                                              user=self.user).exists())

    def test_unfollow_authorized_user(self):
        """Авторизированный пользователь может отписываться на других
        пользователей
        """
        author = PostPagesTests.author
        self.authorized_client.get(reverse(
            "profile_unfollow",
            kwargs={"username": author.username}
        ))
        self.assertFalse(Follow.objects.filter(author=author,
                                               user=self.user).exists())

    def test_post_appearance_in_follow_index(self):
        """Новая запись появится в follow_index только у подписчиков"""
        author = PostPagesTests.author
        post = PostPagesTests.post
        self.authorized_client.get(reverse(
            "profile_follow",
            kwargs={"username": author.username}
        ))
        self.author_client.get(reverse(
            "profile_follow",
            kwargs={"username": self.user.username}
        ))
        response_following_author = self.authorized_client.get(
            reverse("follow_index")
        )
        response_not_following_author = self.author_client.get(
            reverse("follow_index")
        )
        self.assertEqual(response_following_author.context["page"][0], post)
        self.assertNotIn(post, response_not_following_author.context["page"])
