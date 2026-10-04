from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'created_at', 'is_read')
    can_delete = True
    max_num = 30


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group', 'participants_list', 'created_at')
    list_filter = ('is_group', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)
    inlines = [MessageInline]

    @admin.display(description='Учасники')
    def participants_list(self, obj):
        return ', '.join(u.username for u in obj.participants.all()[:5])


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'short_content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'content')
    ordering = ('-created_at',)
    actions = ['delete_selected']

    @admin.display(description='Повідомлення')
    def short_content(self, obj):
        return obj.content[:60] if obj.content else '[медіа]'
