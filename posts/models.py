from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name="Запись",
                            help_text="Напишите что-нибудь здесь.")
    pub_date = models.DateTimeField("date published", auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey("Group", verbose_name="Группа",
                              on_delete=models.SET_NULL, blank=True,
                              null=True, related_name="posts",
                              help_text="Выберите группу,"
                              " или оставьте поле пустым.")
    image = models.ImageField(verbose_name="Картинка",
                              upload_to="posts/", blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name="Пост",
                             on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name="Комментарий",
                            help_text="Оставьте комментарий.")
    created = models.DateTimeField(verbose_name="Дата публикации",
                                   auto_now_add=True)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name="Подписчик",
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="following")
