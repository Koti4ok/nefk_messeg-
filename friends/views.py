from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models as dmodels

from .models import FriendRequest, Friendship, Follow
from accounts.models import User
from notifications.models import Notification


@login_required
def friends_list_view(request):
    friends = Friendship.get_friends(request.user)
    incoming = FriendRequest.objects.filter(
        to_user=request.user, status='pending'
    ).select_related('from_user')
    outgoing = FriendRequest.objects.filter(
        from_user=request.user, status='pending'
    ).select_related('to_user')
    return render(request, 'friends/friends.html', {
        'friends': friends,
        'incoming': incoming,
        'outgoing': outgoing,
    })


@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if to_user == request.user:
        messages.error(request, 'Не можна додати себе в друзі.')
        return redirect('profile', username=username)
    if Friendship.are_friends(request.user, to_user):
        messages.info(request, 'Ви вже друзі.')
        return redirect('profile', username=username)
    req, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=to_user,
        defaults={'status': 'pending'}
    )
    if created:
        Notification.objects.create(
            recipient=to_user,
            sender=request.user,
            notif_type='friend_request',
            text=f'{request.user.get_full_name()} надіслав вам запит у друзі.',
            link=f'/profile/{request.user.username}/'
        )
        messages.success(request, f'Запит надіслано {to_user.get_full_name()}.')
    else:
        messages.info(request, 'Запит вже надіслано.')
    return redirect('profile', username=username)


@login_required
def accept_friend_request(request, request_id):
    freq = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    freq.status = 'accepted'
    freq.save()
    u1 = min(freq.from_user, freq.to_user, key=lambda u: u.id)
    u2 = max(freq.from_user, freq.to_user, key=lambda u: u.id)
    Friendship.objects.get_or_create(user1=u1, user2=u2)
    Notification.objects.create(
        recipient=freq.from_user,
        sender=request.user,
        notif_type='friend_accept',
        text=f'{request.user.get_full_name()} прийняв ваш запит у друзі.',
        link=f'/profile/{request.user.username}/'
    )
    messages.success(request, f'Ви тепер друзі з {freq.from_user.get_full_name()}.')
    return redirect('friends')


@login_required
def decline_friend_request(request, request_id):
    freq = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    freq.status = 'declined'
    freq.save()
    return redirect('friends')


@login_required
def remove_friend(request, username):
    other = get_object_or_404(User, username=username)
    Friendship.objects.filter(
        dmodels.Q(user1=request.user, user2=other) |
        dmodels.Q(user1=other, user2=request.user)
    ).delete()
    FriendRequest.objects.filter(
        dmodels.Q(from_user=request.user, to_user=other) |
        dmodels.Q(from_user=other, to_user=request.user)
    ).delete()
    messages.info(request, f'{other.get_full_name()} видалено з друзів.')
    return redirect('profile', username=username)


@login_required
def follow_user(request, username):
    to_user = get_object_or_404(User, username=username)
    if to_user != request.user:
        Follow.objects.get_or_create(follower=request.user, following=to_user)
        messages.success(request, f'Ви підписались на {to_user.get_full_name()}.')
    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    to_user = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=to_user).delete()
    messages.info(request, f'Ви відписались від {to_user.get_full_name()}.')
    return redirect('profile', username=username)
