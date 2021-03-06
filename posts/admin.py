from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "slug")
    search_fields = ("title", "description")
    list_filter = ("slug",)
    empty_value_display = "-пусто-"


admin.site.register(Group, GroupAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("author", "user")
    empty_value_display = "-пусто-"


admin.site.register(Follow, FollowAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")
    search_fields = ("post", "author")
    list_filter = ("created",)
    empty_value_display = "-пусто-"


admin.site.register(Comment, CommentAdmin)
