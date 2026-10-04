from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Post, Like, Comment
from .forms import PostForm, CommentForm
from friends.models import Friendship, Follow
from notifications.models import Notification


def _create_notification(recipient, sender, notif_type, text, link=''):
    from notifications.models import NotificationSettings
    if recipient == sender:
        return
    try:
        settings = recipient.notification_settings
        if notif_type == 'like' and not settings.notify_likes:
            return
        if notif_type == 'comment' and not settings.notify_comments:
            return
    except Exception:
        pass
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notif_type=notif_type,
        text=text,
        link=link,
    )


@login_required
def feed_view(request):
    user = request.user
    # Збираємо ID друзів та підписок
    friend_ids = list(
        Friendship.get_friends(user).values_list('id', flat=True)
    )
    following_ids = list(
        user.following.values_list('following_id', flat=True)
    )
    author_ids = set(friend_ids + following_ids + [user.id])

    posts = Post.objects.filter(
        author_id__in=author_ids, group=None
    ).select_related('author', 'original_post__author').prefetch_related('likes', 'comments').order_by('-created_at')

    post_form = PostForm()
    comment_form = CommentForm()

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = user
            post.save()
            messages.success(request, 'Публікацію додано.')
            return redirect('feed')

    from accounts.models import User as UserModel
    popular_users = UserModel.objects.exclude(id=user.id).order_by('-date_joined')[:8]

    # Друзі поточного юзера для правого сайдбару
    my_friends = list(Friendship.get_friends(user).select_related()[:8])

    # Pending incoming friend requests count
    from friends.models import FriendRequest
    pending_count = FriendRequest.objects.filter(to_user=user, status='pending').count()

    context = {
        'posts': posts,
        'post_form': post_form,
        'comment_form': comment_form,
        'popular_users': popular_users,
        'my_friends': my_friends,
        'pending_count': pending_count,
    }
    return render(request, 'posts/feed.html', context)


@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            _create_notification(
                post.author, request.user, 'comment',
                f'{request.user.get_full_name()} прокоментував вашу публікацію.',
                f'/posts/{post.pk}/'
            )
            return redirect('post_detail', pk=pk)

    comments = post.comments.select_related('author').all()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
@require_POST
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        _create_notification(
            post.author, request.user, 'like',
            f'{request.user.get_full_name()} вподобав вашу публікацію.',
            f'/posts/{post.pk}/'
        )
    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
@require_POST
def repost_view(request, pk):
    original = get_object_or_404(Post, pk=pk)
    Post.objects.create(
        author=request.user,
        content=original.content,
        post_type=original.post_type,
        original_post=original,
    )
    _create_notification(
        original.author, request.user, 'repost',
        f'{request.user.get_full_name()} поширив вашу публікацію.',
        f'/posts/{original.pk}/'
    )
    messages.success(request, 'Публікацію поширено.')
    return redirect('feed')


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user or request.user.is_admin_role():
        post.delete()
        messages.success(request, 'Публікацію видалено.')
    return redirect(request.META.get('HTTP_REFERER', 'feed'))
