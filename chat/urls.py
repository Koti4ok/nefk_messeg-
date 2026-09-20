from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.conversations_view, name='conversations'),
    # group/create/ перед <int:pk>/ щоб уникнути конфлікту
    path('chat/group/create/', views.create_group_chat_view, name='create_group_chat'),
    path('chat/<int:pk>/', views.conversation_view, name='conversation'),
    path('chat/<int:pk>/messages/', views.get_new_messages, name='get_new_messages'),
]
