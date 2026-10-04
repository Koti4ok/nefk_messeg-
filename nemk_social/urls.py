from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accounts.models import User
from groups.models import Group
from .chatbot_views import chatbot_api
from .translate_view import translate_view
from .security import security_dashboard, security_stats_api


def home_view(request):
    if request.user.is_authenticated:
        from posts.views import feed_view
        return feed_view(request)
    # Популярні користувачі та групи для гостей
    popular_users = User.objects.order_by('-date_joined')[:6]
    popular_groups = Group.objects.order_by('-created_at')[:4]
    return render(request, 'home.html', {
        'popular_users': popular_users,
        'popular_groups': popular_groups,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
    path('api/translate/', translate_view, name='translate_api'),
    path('api/security/stats/', security_stats_api, name='security_stats_api'),
    path('security/dashboard/', security_dashboard, name='security_dashboard'),
    path('', include('accounts.urls')),
    path('', include('posts.urls')),
    path('', include('friends.urls')),
    path('', include('groups.urls')),
    path('', include('chat.urls')),
    path('', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
