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
    path('units/', web_views.unit_list, name='unit_list'),
    path('units/create/', web_views.create_unit, name='create_unit'),
    path('units/<int:unit_id>/toggle/', web_views.toggle_unit_status, name='toggle_unit_status'),
    path('divisions/create/', web_views.create_division, name='create_division'),
    path('divisions/', web_views.division_list, name='division_list'),
    path('ajax/units-by-group/', web_views.get_units_by_group, name='get_units_by_group'),
]
