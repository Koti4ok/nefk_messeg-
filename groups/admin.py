from django.contrib import admin
from django.utils.html import format_html
from .models import Group, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    fields = ('user', 'role', 'is_active', 'joined_at')
    readonly_fields = ('joined_at',)
    can_delete = True


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'member_count', 'is_private', 'avatar_preview', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('name', 'creator__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    inlines = [GroupMembershipInline]

    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="36" height="36" style="border-radius:50%;object-fit:cover;">',
                obj.avatar.url
            )
        return '—'

    @admin.display(description='Учасники')
    def member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'group__name')
    list_editable = ('role', 'is_active')
