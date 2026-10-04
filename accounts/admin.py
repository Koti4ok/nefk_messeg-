from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'avatar_preview', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    list_editable = ('role', 'is_active')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Профіль', {
            'fields': ('role', 'avatar', 'cover', 'bio', 'location', 'birth_date', 'website')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Профіль', {
            'fields': ('email', 'first_name', 'last_name', 'role')
        }),
    )

    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="36" height="36" style="border-radius:50%;object-fit:cover;">',
                obj.avatar.url
            )
        return '—'

    @admin.action(description='✅ Призначити адміністратором (role=admin + is_staff + is_superuser)')
    def make_admin(self, request, queryset):
        queryset.update(role='admin', is_staff=True, is_superuser=True)
        self.message_user(request, f'{queryset.count()} користувачів отримали права адміністратора.')

    @admin.action(description='🚫 Зняти права адміністратора (role=user)')
    def revoke_admin(self, request, queryset):
        queryset.update(role='user', is_staff=False, is_superuser=False)
        self.message_user(request, f'{queryset.count()} користувачів понижено до ролі Користувач.')

    actions = ['make_admin', 'revoke_admin']
