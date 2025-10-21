
# apps/accounts/web_urls.py   (web)
from django.urls import path
from django.contrib.auth.views import LogoutView
from .web_views import web_login_view, web_register_view, web_profile_view, web_change_password_view
from . import web_views

app_name = 'accounts'

urlpatterns = [
    path('login/', web_login_view, name='login'),
    path('register/', web_register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/', web_profile_view, name='profile'),
    path('change-password/', web_change_password_view, name='change-password'),
    path("groups/create/", web_views.create_group, name="create_group"),
    path('groups/', web_views.group_list, name='group_list'),
]



