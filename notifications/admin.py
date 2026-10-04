from django.contrib import admin
from .models import Notification, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'notif_type', 'short_text', 'is_read', 'created_at')
    list_filter = ('notif_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'text')
    ordering = ('-created_at',)
    list_editable = ('is_read',)
    actions = ['mark_as_read', 'delete_selected']

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:60]

    @admin.action(description='Позначити як прочитані')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'notify_friend_request',
        'notify_likes',
        'notify_comments',
        'notify_messages',
        'notify_group_invites',
    )
    search_fields = ('user__username',)
