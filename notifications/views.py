from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Notification, NotificationSettings
from .forms import NotificationSettingsForm


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender').order_by('-created_at')[:50]
    # Позначити як прочитані
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/notifications.html', {'notifs': notifs})


@login_required
def notifications_settings_view(request):
    settings_obj, _ = NotificationSettings.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Налаштування збережено.')
            return redirect('notifications')
    else:
        form = NotificationSettingsForm(instance=settings_obj)
    return render(request, 'notifications/settings.html', {'form': form})


@login_required
def unread_count_view(request):
    """AJAX — кількість непрочитаних сповіщень."""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})
