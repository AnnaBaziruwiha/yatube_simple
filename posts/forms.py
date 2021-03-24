from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["group", "text", "image"]
        error_messages = {
            "text": {
                "required": "Вы пытаетесь отправить пустую запись",
            },
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        error_messages = {
            "text": {
                "required": "Вы пытаетесь отправить пустую запись",
            },
        }
