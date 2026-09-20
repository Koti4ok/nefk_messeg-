from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'Користувач'),
        (ROLE_ADMIN, 'Адміністратор'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=120, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    def save(self, *args, **kwargs):
        # Адміністратори автоматично отримують права Django staff/superuser
        if self.role == self.ROLE_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        else:
            # Якщо знизили роль — забираємо права (якщо не встановлено вручну через окреме поле)
            if not self._state.adding:  # тільки при оновленні, не при створенні
                # Перевіряємо попередній стан
                try:
                    old = User.objects.get(pk=self.pk)
                    if old.role == self.ROLE_ADMIN and self.role != self.ROLE_ADMIN:
                        self.is_staff = False
                        self.is_superuser = False
                except User.DoesNotExist:
                    pass
        super().save(*args, **kwargs)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default_avatar.svg'

    def get_cover_url(self):
        if self.cover:
            return self.cover.url
        return '/static/img/default_cover.svg'

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'
