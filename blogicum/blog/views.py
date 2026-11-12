from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .constants import POSTS_BY_PAGE
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post

User = get_user_model()


def paginate_posts(request, post_list):
    paginator = Paginator(post_list, POSTS_BY_PAGE)
    return paginator.get_page(request.GET.get('page', 1))


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
        'page_obj': paginate_posts(request, post_list),
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
        'page_obj': paginate_posts(request, post_list),
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    post_list = profile_user.posts.with_related()

    if request.user != profile_user:
        post_list = post_list.published()

    context = {
        'profile': profile_user,
        'page_obj': paginate_posts(request, post_list),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None,
        instance=request.user,
    )

    if not form.is_valid():
        return render(
            request,
            'blog/user.html',
            {'form': form},
        )

    form.save()
    return redirect(
        'blog:profile',
        username=request.user.username,
    )


@login_required
def create_post(request):
    form = PostForm(
        request.POST or None,
        request.FILES or None,
    )

    if not form.is_valid():
        return render(
            request,
            'blog/create.html',
            {'form': form},
        )

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(
        'blog:profile',
        username=request.user.username,
    )


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=post.pk)

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )

    if not form.is_valid():
        return render(
            request,
            'blog/create.html',
            {'form': form},
        )

    form.save()
    return redirect('blog:post_detail', id=post.pk)


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

    if request.method != 'POST':
        return redirect('blog:post_detail', id=post.pk)

    form = CommentForm(request.POST or None)

    if not form.is_valid():
        context = {
            'post': post,
            'form': form,
            'comments': post.comments.select_related('author'),
        }
        return render(request, 'blog/detail.html', context)

    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
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

    form = CommentForm(
        request.POST or None,
        instance=comment,
    )

    if not form.is_valid():
        context = {
            'comment': comment,
            'form': form,
        }
        return render(request, 'blog/comment.html', context)

    form.save()
    return redirect('blog:post_detail', id=post_id)


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
