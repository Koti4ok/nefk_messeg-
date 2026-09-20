from django.db import models
from django.conf import settings
from django.utils import timezone


class FriendRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Очікує'),
        (STATUS_ACCEPTED, 'Прийнято'),
        (STATUS_DECLINED, 'Відхилено'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_requests', verbose_name='Від'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='received_requests', verbose_name='Кому'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name = 'Запит у друзі'
        verbose_name_plural = 'Запити у друзі'

    def __str__(self):
        return f'{self.from_user} → {self.to_user} ({self.status})'


class Friendship(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='friendships_as_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='friendships_as_user2'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user1', 'user2')
        verbose_name = 'Дружба'
        verbose_name_plural = 'Друзі'

    def __str__(self):
        return f'{self.user1} ↔ {self.user2}'

    @classmethod
    def are_friends(cls, u1, u2):
        return cls.objects.filter(
            models.Q(user1=u1, user2=u2) | models.Q(user1=u2, user2=u1)
        ).exists()

    @classmethod
    def get_friends(cls, user):
        from django.conf import settings
        User = settings.AUTH_USER_MODEL
        qs1 = cls.objects.filter(user1=user).values_list('user2', flat=True)
        qs2 = cls.objects.filter(user2=user).values_list('user1', flat=True)
        from accounts.models import User as UserModel
        ids = list(qs1) + list(qs2)
        return UserModel.objects.filter(id__in=ids)


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='following', verbose_name='Підписник'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='followers', verbose_name='На кого підписаний'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Підписка'
        verbose_name_plural = 'Підписки'

    def __str__(self):
        return f'{self.follower} → {self.following}'
