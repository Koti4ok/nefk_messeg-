from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/settings/', views.notifications_settings_view, name='notification_settings'),
    path('notifications/unread/', views.unread_count_view, name='unread_count'),
]
