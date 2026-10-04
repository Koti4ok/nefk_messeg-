from django.urls import path
from . import views

urlpatterns = [
    path('friends/', views.friends_list_view, name='friends'),
    path('friends/request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/remove/<str:username>/', views.remove_friend, name='remove_friend'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
]
