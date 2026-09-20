from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # edit_profile має бути ПЕРЕД profile/<username>/ щоб Django не сприйняв 'edit' як username
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('search/', views.search_users_view, name='search_users'),
]
