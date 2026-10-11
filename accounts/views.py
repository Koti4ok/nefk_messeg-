from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from .models import User
from .forms import RegisterForm, LoginForm, ProfileEditForm
from posts.models import Post
from groups.models import Group
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
            if not request.user.is_superuser:
                user.role = request.user.role
            user.save()
            messages.success(request, 'Профіль оновлено.')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


# ─── Fuzzy helpers ────────────────────────────────────────────────────────────

def _fuzzy_tokens(query):
    """
    Генерує варіанти запиту враховуючи типові помилки в українській:
    и/і, е/є, ї/і, г/ґ, ь на кінці + видалення одного символу.
    """
    raw = query.lower().strip()
    replacements = [
        ('і', 'и'), ('и', 'і'),
        ('є', 'е'), ('е', 'є'),
        ('ї', 'і'), ('і', 'ї'),
        ('ґ', 'г'), ('г', 'ґ'),
        ('ь', ''),
    ]
    variants = {raw}
    for old, new in replacements:
        variants.add(raw.replace(old, new))
    # Видалення одного символу (помилки типу «Максим» → «Маским»)
    if len(raw) > 3:
        for i in range(len(raw)):
            v = raw[:i] + raw[i + 1:]
            if v:
                variants.add(v)
    return list(variants)


def _build_user_q(variants):
    q = Q()
    for v in variants:
        q |= (Q(username__icontains=v) | Q(first_name__icontains=v) |
              Q(last_name__icontains=v) | Q(bio__icontains=v) | Q(location__icontains=v))
    return q


def _build_post_q(variants):
    q = Q()
    for v in variants:
        q |= Q(content__icontains=v)
    return q


def _build_group_q(variants):
    q = Q()
    for v in variants:
        q |= Q(name__icontains=v) | Q(description__icontains=v)
    return q


# ─── Сторінка пошуку ──────────────────────────────────────────────────────────

@login_required
def search_users_view(request):
    query = request.GET.get('q', '').strip()
    tab   = request.GET.get('tab', 'users')
    users, posts, groups = [], [], []

    if query:
        variants = _fuzzy_tokens(query)

        users = (User.objects
                 .filter(_build_user_q(variants))
                 .exclude(id=request.user.id)
                 .distinct()[:20])

        posts = (Post.objects
                 .filter(_build_post_q(variants))
                 .select_related('author', 'group')
                 .order_by('-created_at')
                 .distinct()[:20])

        groups = (Group.objects
                  .filter(_build_group_q(variants))
                  .filter(is_private=False)
                  .distinct()[:20])

    return render(request, 'accounts/search.html', {
        'query':        query,
        'tab':          tab,
        'users':        users,
        'posts':        posts,
        'groups':       groups,
        'users_count':  len(users),
        'posts_count':  len(posts),
        'groups_count': len(groups),
    })


# ─── AJAX endpoint для live-dropdown ─────────────────────────────────────────

@login_required
def search_ajax_view(request):
    """
    Повертає JSON для live-dropdown в navbar.
    GET /api/search/?q=...
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': [], 'posts': [], 'groups': [], 'query': query})

    variants = _fuzzy_tokens(query)

    # Юзери
    users_qs = (User.objects
                .filter(_build_user_q(variants))
                .exclude(id=request.user.id)
                .distinct()[:5])
    users_data = [{
        'username':  u.username,
        'full_name': u.get_full_name() or u.username,
        'avatar':    u.get_avatar_url(),
        'url':       f'/profile/{u.username}/',
    } for u in users_qs]

    # Пости
    posts_qs = (Post.objects
                .filter(_build_post_q(variants))
                .select_related('author')
                .order_by('-created_at')
                .distinct()[:5])
    posts_data = [{
        'id':            p.id,
        'content':       p.content[:90] + ('…' if len(p.content) > 90 else ''),
        'author':        p.author.get_full_name() or p.author.username,
        'author_avatar': p.author.get_avatar_url(),
        'url':           f'/posts/{p.id}/',
    } for p in posts_qs]

    # Групи
    groups_qs = (Group.objects
                 .filter(_build_group_q(variants))
                 .filter(is_private=False)
                 .distinct()[:5])
    groups_data = [{
        'id':      g.id,
        'name':    g.name,
        'avatar':  g.get_avatar_url(),
        'members': g.member_count(),
        'url':     f'/groups/{g.id}/',
    } for g in groups_qs]

    return JsonResponse({
        'query':  query,
        'users':  users_data,
        'posts':  posts_data,
        'groups': groups_data,
    })
