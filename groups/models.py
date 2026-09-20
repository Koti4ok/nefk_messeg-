from django.db import models
from django.conf import settings
from django.utils import timezone


class Group(models.Model):
    name = models.CharField(max_length=150, verbose_name='Назва')
    description = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='groups/avatars/', blank=True, null=True)
    cover = models.ImageField(upload_to='groups/covers/', blank=True, null=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_groups', verbose_name='Засновник'
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_private = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Група'
        verbose_name_plural = 'Групи'

    def __str__(self):
        return self.name

    def member_count(self):
        return self.memberships.filter(is_active=True).count()

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default_group.svg'


class GroupMembership(models.Model):
    ROLE_MEMBER = 'member'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_MEMBER, 'Учасник'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Адміністратор'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('group', 'user')
        verbose_name = 'Учасник групи'
        verbose_name_plural = 'Учасники груп'

    def __str__(self):
        return f'{self.user} в {self.group} ({self.role})'
