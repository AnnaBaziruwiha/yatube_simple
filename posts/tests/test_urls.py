from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username="author",
            password="123"
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test",
            description="Группа для теста"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            group=cls.group,
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="test_user")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = PostUrlTests.author
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_wrong_url_returns_404(self):
        """Сервер возвращает 404 если страница не найдена"""
        response = self.guest_client.get("/this/url/is/wrong/")
        self.assertEqual(response.status_code, 404)

    def test_homepage(self):
        """Страница / доступна любому пользователю"""
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_group_slug_exists_at_desired_location(self):
        """Страница /group/<slug>/ доступна любому пользователю"""
        group_slug = PostUrlTests.group.slug
        response = self.guest_client.get(f"/group/{group_slug}/")
        self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location_authorized(self):
        """Страница /new/ доступна авторизированному пользователю"""
        response = self.authorized_client.get("/new/")
        self.assertEqual(response.status_code, 200)

    def test_new_url_redirect_anonymous_to_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get("/new/", follow=True)
        self.assertRedirects(
            response, ("/auth/login/?next=/new/")
        )

    def test_profile_page(self):
        """Страница /<username>/ доступна любому пользователю"""
        username = PostUrlTests.author.username
        response = self.guest_client.get(f"/{username}/")
        self.assertEqual(response.status_code, 200)

    def test_post_page(self):
        """Страница /<username>/<post_id>/ доступна любому пользователю"""
        post = PostUrlTests.post
        username = post.author.username
        response = self.guest_client.get(f"/{username}/{post.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_post_edit_by_author(self):
        """Страница /<username>/<post_id>/edit доступна автору поста"""
        post = PostUrlTests.post
        username = post.author.username
        response = self.author_client.get(f"/{username}/{post.pk}/edit/")
        self.assertEqual(response.status_code, 200)

    def test_post_edit_by_authorized_not_author(self):
        """Страница /<username>/<post_id>/edit перенаправит всех кроме
        автора поста
        """
        post = PostUrlTests.post
        username = post.author.username
        client_redirect = {
            self.authorized_client: f"/{username}/{post.pk}/",
            self.guest_client: ("/auth/login/?next="
                                f"/{username}/{post.pk}/edit/"),
        }
        for client, redirect in client_redirect.items():
            with self.subTest(redirect=redirect):
                response = client.get(f"/{username}/{post.pk}/edit/",
                                      follow=True)
                self.assertRedirects(response, redirect)

    def test_url_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        post = PostUrlTests.post
        group_slug = PostUrlTests.group.slug
        username = post.author.username
        url_templates = {
            f"/group/{group_slug}/": "posts/group.html",
            "/new/": "posts/new.html",
            "/": "posts/index.html",
            f"/{username}/{post.pk}/edit/": "posts/new.html",
        }
        for url, template in url_templates.items():
            with self.subTest(template=template):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
