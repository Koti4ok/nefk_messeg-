from django.db import models
from django.conf import settings
from django.utils import timezone


class Post(models.Model):
    POST_TYPE_STATUS = 'status'
    POST_TYPE_PHOTO = 'photo'
    POST_TYPE_VIDEO = 'video'
    POST_TYPE_LINK = 'link'
    POST_TYPE_CHOICES = [
        (POST_TYPE_STATUS, 'Статус'),
        (POST_TYPE_PHOTO, 'Фото'),
        (POST_TYPE_VIDEO, 'Відео'),
        (POST_TYPE_LINK, 'Посилання'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='posts', verbose_name='Автор'
    )
    group = models.ForeignKey(
        'groups.Group', on_delete=models.CASCADE,
        related_name='posts', null=True, blank=True,
        verbose_name='Група'
    )
    post_type = models.CharField(
        max_length=10, choices=POST_TYPE_CHOICES,
        default=POST_TYPE_STATUS, verbose_name='Тип'
    )
    content = models.TextField(verbose_name='Текст')
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    link = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Репост
    original_post = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reposts'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'{self.user.username} → {self.post.id}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name='Коментар')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'

    def __str__(self):
        return f'{self.author.username}: {self.content[:40]}'


class Rating(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(default=5)  # 1-5
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = 'Оцінка'
        verbose_name_plural = 'Оцінки'
