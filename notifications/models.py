from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    TYPE_FRIEND_REQUEST = 'friend_request'
    TYPE_FRIEND_ACCEPT = 'friend_accept'
    TYPE_LIKE = 'like'
    TYPE_COMMENT = 'comment'
    TYPE_MESSAGE = 'message'
    TYPE_GROUP_INVITE = 'group_invite'
    TYPE_REPOST = 'repost'
    TYPE_CHOICES = [
        (TYPE_FRIEND_REQUEST, 'Запит у друзі'),
        (TYPE_FRIEND_ACCEPT, 'Прийнято в друзі'),
        (TYPE_LIKE, 'Лайк'),
        (TYPE_COMMENT, 'Коментар'),
        (TYPE_MESSAGE, 'Повідомлення'),
        (TYPE_GROUP_INVITE, 'Запрошення до групи'),
        (TYPE_REPOST, 'Репост'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name='Отримувач'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_notifications', null=True, blank=True
    )
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text = models.CharField(max_length=255, blank=True, default='')
    link = models.CharField(max_length=255, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сповіщення'
        verbose_name_plural = 'Сповіщення'

    def __str__(self):
        return f'{self.recipient.username} ← {self.notif_type}'


class NotificationSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    notify_friend_request = models.BooleanField(default=True)
    notify_likes = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True)
    notify_group_invites = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Налаштування сповіщень'
        verbose_name_plural = 'Налаштування сповіщень'
