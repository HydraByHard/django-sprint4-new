from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .constants import POSTS_BY_PAGE
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post

User = get_user_model()


def get_page_obj(request, post_list):
    paginator = Paginator(post_list, POSTS_BY_PAGE)
    return paginator.get_page(request.GET.get('page'))


def get_post(request, post_id):
    posts = Post.objects.with_related()
    post = get_object_or_404(posts, pk=post_id)

    if request.user != post.author:
        post = get_object_or_404(
            posts.published(),
            pk=post_id,
        )

    return post


def index(request):
    post_list = Post.objects.with_related().published()

    context = {
        'page_obj': get_page_obj(request, post_list),
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_post(request, id)

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author'),
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    post_list = (
        Post.objects.with_related()
        .published()
        .filter(category=category)
    )

    context = {
        'category': category,
        'page_obj': get_page_obj(request, post_list),
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    post_list = profile_user.posts.with_related()

    if request.user != profile_user:
        post_list = post_list.published()

    context = {
        'profile': profile_user,
        'page_obj': get_page_obj(request, post_list),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(
                'blog:profile',
                username=request.user.username,
            )
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(
                'blog:profile',
                username=request.user.username,
            )
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=post.pk)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=post.pk)

    if request.method == 'POST':
        post.delete()
        return redirect(
            'blog:profile',
            username=request.user.username,
        )

    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_post(request, post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=post.pk)

        context = {
            'post': post,
            'form': form,
            'comments': post.comments.select_related('author'),
        }
        return render(request, 'blog/detail.html', context)

    return redirect('blog:post_detail', id=post.pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post_id=post_id,
    )

    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'comment': comment,
        'form': form,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post_id=post_id,
    )

    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    context = {
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)
