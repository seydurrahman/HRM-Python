from django.urls import path
from django.contrib.auth.views import LogoutView
from . import web_views

app_name = 'accounts'

urlpatterns = [
    path('login/', web_views.web_login_view, name='login'),
    path('register/', web_views.web_register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/', web_views.web_profile_view, name='profile'),
    path('change-password/', web_views.web_change_password_view, name='change-password'),

    # Group management
    path('groups/', web_views.group_list, name='group_list'),
    path('groups/create/', web_views.create_group, name='create_group'),
    path('groups/<int:group_id>/toggle/', web_views.toggle_group_status, name='toggle_group_status'),
]
