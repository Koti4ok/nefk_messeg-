from django.urls import path
from . import views

urlpatterns = [
    path('groups/', views.groups_list_view, name='groups'),
    path('groups/create/', views.create_group_view, name='create_group'),
    path('groups/<int:pk>/', views.group_detail_view, name='group_detail'),
    path('groups/<int:pk>/join/', views.join_group_view, name='join_group'),
    path('groups/<int:pk>/leave/', views.leave_group_view, name='leave_group'),
    path('groups/<int:pk>/kick/<int:user_id>/', views.kick_member_view, name='kick_member'),
]
