from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import User
from .forms import RegisterForm, LoginForm, ProfileEditForm
from posts.models import Post
from friends.models import FriendRequest, Friendship, Follow
from notifications.models import NotificationSettings


def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            NotificationSettings.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Вітаємо, {user.first_name}! Ваш акаунт створено.')
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)
        else:
            messages.error(request, 'Неправильний логін або пароль.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user, group=None).order_by('-created_at')

    is_self = request.user == profile_user
    are_friends = Friendship.are_friends(request.user, profile_user) if not is_self else False
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists() if not is_self else False

    pending_request = None
    if not is_self and not are_friends:
        pending_request = FriendRequest.objects.filter(
            from_user=request.user, to_user=profile_user, status='pending'
        ).first()

    friends = Friendship.get_friends(profile_user)[:6]
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_self': is_self,
        'are_friends': are_friends,
        'is_following': is_following,
        'pending_request': pending_request,
        'friends': friends,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # Тільки адміністратори можуть міняти роль через адмін-панель,
            # тут примусово залишаємо поточну роль (захист від підміни)
            if not request.user.is_superuser:
                user.role = request.user.role
            user.save()
            messages.success(request, 'Профіль оновлено.')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def search_users_view(request):
    query = request.GET.get('q', '').strip()
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:20]
    return render(request, 'accounts/search.html', {'users': users, 'query': query})
