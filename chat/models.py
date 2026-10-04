from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='conversations'
    )
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=150, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Розмова'
        verbose_name_plural = 'Розмови'

    def __str__(self):
        if self.name:
            return self.name
        return f'Розмова #{self.id}'

    def get_name_for(self, user):
        if self.name:
            return self.name
        other = self.participants.exclude(id=user.id).first()
        return other.username if other else 'Розмова'

    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages'
    )
    content = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='chat/files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    video = models.FileField(upload_to='chat/videos/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'

    def __str__(self):
        return f'{self.sender.username}: {self.content[:40]}'
