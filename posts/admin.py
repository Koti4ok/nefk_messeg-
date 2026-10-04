from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Like, Comment, Rating


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    readonly_fields = ('user', 'created_at')
    can_delete = True


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'content', 'created_at')
    can_delete = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post_type', 'short_content', 'group', 'like_count', 'comment_count', 'created_at')
    list_filter = ('post_type', 'created_at', 'group')
    search_fields = ('author__username', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'like_count', 'comment_count')
    inlines = [LikeInline, CommentInline]
    actions = ['delete_selected']

    @admin.display(description='Текст')
    def short_content(self, obj):
        return obj.content[:60] + ('…' if len(obj.content) > 60 else '')

    @admin.display(description='Лайки')
    def like_count(self, obj):
        return obj.likes.count()

    @admin.display(description='Коментарі')
    def comment_count(self, obj):
        return obj.comments.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'short_content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'content')
    ordering = ('-created_at',)
    actions = ['delete_selected']

    @admin.display(description='Текст')
    def short_content(self, obj):
        return obj.content[:60]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('user__username',)
