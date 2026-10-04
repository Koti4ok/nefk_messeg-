from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Conversation, Message
from .forms import MessageForm, NewConversationForm
from accounts.models import User


def _get_conv_name(conv, user):
    """Повертає відображувану назву розмови для конкретного юзера."""
    if conv.name:
        return conv.name
    if conv.is_group:
        return f'Груповий чат #{conv.pk}'
    other = conv.participants.exclude(id=user.id).first()
    if other:
        return other.get_full_name() or other.username
    return f'Розмова #{conv.pk}'


@login_required
def conversations_view(request):
    raw_convs = request.user.conversations.prefetch_related('participants').order_by('-created_at')
    # Анотуємо кожну розмову відображуваним ім'ям
    conversations = []
    for conv in raw_convs:
        conv.other_name = _get_conv_name(conv, request.user)
        conversations.append(conv)

    new_form = NewConversationForm()

    if request.method == 'POST' and 'start_chat' in request.POST:
        new_form = NewConversationForm(request.POST)
        if new_form.is_valid():
            username = new_form.cleaned_data['username']
            try:
                other = User.objects.get(username=username)
                if other == request.user:
                    messages.error(request, 'Не можна написати самому собі.')
                else:
                    existing = Conversation.objects.filter(
                        participants=request.user, is_group=False
                    ).filter(participants=other).first()
                    if existing:
                        return redirect('conversation', pk=existing.pk)
                    conv = Conversation.objects.create(is_group=False)
                    conv.participants.add(request.user, other)
                    return redirect('conversation', pk=conv.pk)
            except User.DoesNotExist:
                messages.error(request, 'Користувача не знайдено.')

    return render(request, 'chat/conversations.html', {
        'conversations': conversations,
        'new_form': new_form,
    })


@login_required
def conversation_view(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user not in conversation.participants.all():
        messages.error(request, 'Немає доступу до цієї розмови.')
        return redirect('conversations')

    # Позначаємо повідомлення як прочитані
    conversation.messages.exclude(sender=request.user).update(is_read=True)

    chat_messages = conversation.messages.select_related('sender').all()
    form = MessageForm()
    conv_name = _get_conv_name(conversation, request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conversation
            msg.sender = request.user
            msg.save()
            # Сповіщення
            from notifications.models import Notification
            for participant in conversation.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    recipient=participant,
                    sender=request.user,
                    notif_type='message',
                    text=f'Нове повідомлення від {request.user.get_full_name() or request.user.username}',
                    link=f'/chat/{conversation.pk}/'
                )
            # AJAX-відповідь
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': msg.id,
                    'content': msg.content,
                    'sender': msg.sender.username,
                    'sender_name': msg.sender.get_full_name() or msg.sender.username,
                    'avatar': msg.sender.get_avatar_url(),
                    'time': msg.created_at.strftime('%H:%M'),
                })
            return redirect('conversation', pk=pk)

    return render(request, 'chat/conversation.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'form': form,
        'conv_name': conv_name,
    })


@login_required
def create_group_chat_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        user_ids = request.POST.getlist('users')
        if not name:
            messages.error(request, 'Введіть назву групового чату.')
            return redirect('conversations')
        conv = Conversation.objects.create(is_group=True, name=name)
        conv.participants.add(request.user)
        for uid in user_ids:
            try:
                u = User.objects.get(id=uid)
                conv.participants.add(u)
            except User.DoesNotExist:
                pass
        messages.success(request, f'Груповий чат «{name}» створено.')
        return redirect('conversation', pk=conv.pk)

    from friends.models import Friendship
    friends = Friendship.get_friends(request.user)
    return render(request, 'chat/create_group_chat.html', {'friends': friends})


@login_required
def get_new_messages(request, pk):
    """AJAX — підвантаження нових повідомлень (fallback без WebSocket)."""
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'forbidden'}, status=403)
    last_id = int(request.GET.get('last_id', 0))
    new_msgs = conversation.messages.filter(id__gt=last_id).select_related('sender')
    data = [{
        'id': m.id,
        'content': m.content,
        'sender': m.sender.username,
        'sender_name': m.sender.get_full_name() or m.sender.username,
        'avatar': m.sender.get_avatar_url(),
        'time': m.created_at.strftime('%H:%M'),
        'is_me': m.sender == request.user,
    } for m in new_msgs]
    return JsonResponse({'messages': data})
