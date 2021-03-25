from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from yatube.settings import PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, PER_PAGE)

    page_number = request.GET.get("page")

    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PER_PAGE)

    page_number = request.GET.get("page")

    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {"group": group,
                                                "page": page,
                                                "paginator": paginator})


@login_required
def new_post(request):
    new_post = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "posts/new.html",
                  {"new_post": new_post, "form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=author,
                                          user=request.user).exists()
        return render(request, "posts/profile.html", {
            "author": author, "posts": posts,
            "page": page, "following": following
        })
    return render(
        request,
        "posts/profile.html",
        {"author": author, "posts": posts, "page": page}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post.objects.filter(author__username=username),
                             pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=User.objects.get(username=username),
            user=request.user
        ).exists()
        return render(request, "posts/post.html",
                      {"author": post.author,
                       "posts": post.author.posts.all(),
                       "post": post,
                       "comments": comments,
                       "form": form,
                       "following": following})
    return render(request, "posts/post.html", {
        "author": post.author,
        "posts": post.author.posts.all(),
        "post": post,
        "comments": comments,
        "form": form,
    })


@login_required
def post_edit(request, username, post_id):
    new_post = False
    url = reverse("post", kwargs={"username": username,
                                  "post_id": post_id})
    post = get_object_or_404(Post.objects.filter(author__username=username),
                             pk=post_id)
    if request.user.id != post.author.id:
        return redirect(url)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(url)
    return render(request, "posts/new.html", {"username": username,
                                              "post_id": post_id,
                                              "new_post": new_post,
                                              "post": post,
                                              "form": form})


@login_required
def add_comment(request, username, post_id):
    url = reverse("post", kwargs={"username": username,
                                  "post_id": post_id})
    post = Post.objects.filter(author__username=username, pk=post_id).get()
    comments = post.comments.all()
    form = CommentForm(
        request.POST or None
    )
    following = Follow.objects.filter(
        author=User.objects.get(username=username),
        user=request.user
    ).exists()
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(url)
    return render(request, "posts/post.html", {
        "author": post.author,
        "posts": post.author.posts.all(),
        "post": post,
        "form": form,
        "comments": comments,
        "following": following
    })


@login_required
def follow_index(request):
    user = request.user
    is_following = user.follower.all()
    list_of_authors = [item.author for item in is_following]
    posts = Post.objects.filter(author__in=list_of_authors)

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html",
                  {"page": page, "paginator": paginator})


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user == author:
        return redirect(reverse("follow_index"))
    is_following = Follow.objects.filter(user=request.user, author=author)
    if not is_following:
        Follow.objects.create(user=request.user, author=author)
    return redirect(reverse("follow_index"))


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if request.user == author:
        return redirect(reverse("follow_index"))
    is_following = Follow.objects.filter(user=request.user, author=author)
    if is_following:
        is_following.delete()
    return redirect(reverse("follow_index"))


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
