from django.urls import path
from django.contrib.auth.views import LogoutView
from .web_views import login_view, register_view, profile_view

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/', profile_view, name='profile'),
]