from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.feed_view, name='feed'),
    path('posts/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('posts/<int:pk>/like/', views.like_post_view, name='like_post'),
    path('posts/<int:pk>/repost/', views.repost_view, name='repost'),
    path('posts/<int:pk>/delete/', views.delete_post_view, name='delete_post'),
]
