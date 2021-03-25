import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEST_DIR = "test_data"


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username="Тестовый автор",
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
            author=cls.author,
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
        self.user = PostFormTest.author
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_form_creates_post_in_db(self):
        """Новый пост сохраняется в базе данных"""
        posts_count = Post.objects.count()
        group_pk = PostFormTest.group.pk
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
        form_data = {
            "group": group_pk,
            "text": "Тестовая запись",
            "image": uploaded,
        }
        self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        new_posts_count = Post.objects.count()
        self.assertEqual(posts_count, (new_posts_count - 1))
        self.assertTrue(
            Post.objects.filter(
                group=group_pk,
                text="Тестовая запись",
                image="posts/small.gif"
            ).exists()
        )

    def test_form_modifies_post_in_db(self):
        """При редактировании изменяется соответствующий пост в базе данных"""
        group_pk = PostFormTest.group.pk
        initial_post = PostFormTest.post
        form_data = {
            "group": group_pk,
            "text": "Измененный текст",
        }
        self.authorized_client.post(
            reverse("post_edit",
                    kwargs={
                        "username": PostFormTest.author.username,
                        "post_id": initial_post.pk}),
            data=form_data,
            follow=True
        )
        initial_post.refresh_from_db()
        self.assertEqual(initial_post.text, form_data["text"])
        self.assertEqual(initial_post.group.pk, form_data["group"])


def test_anonymous_cant_comment(self):
    """Только авторизированный пользователь может комментировать"""
    post = PostFormTest.post
    author = post.author
    before_comment = post.comments.count()
    form_data = {
        "text": "тестовый комментарий",
    }
    self.authorized_client.post(
        reverse("add_comment",
                kwargs={
                    "username": author.username,
                    "post_id": post.pk}),
        form_data,
        follow=True
    )
    after_authorized_comment = post.comments.count()
    form_data_anonym = {
        "text": "анонимный комментарий",
    }
    self.guest_client.post(
        reverse("add_comment",
                kwargs={
                    "username": author.username,
                    "post_id": post.pk}),
        form_data_anonym,
        follow=True
    )
    after_anonymous_comment = post.comments.count()
    self.assertEqual(after_authorized_comment, (before_comment + 1))
    self.assertEqual(after_authorized_comment, after_anonymous_comment)
    self.assertTrue(
        Comment.objects.filter(text="тестовый комментарий").exists()
    )
    self.assertFalse(
        Comment.objects.filter(text="анонимный комментарий").exists()
    )
