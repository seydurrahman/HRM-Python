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
    path('ajax/units-by-group/', web_views.get_units_by_group, name='get_units_by_group'),
    path('divisions/create/', web_views.create_division, name='create_division'),
    path('divisions/', web_views.division_list, name='division_list'),
    path('divisions/<int:division_id>/toggle/', web_views.toggle_division_status, name='toggle_division_status'),
    path("ajax/divisions-by-unit/", web_views.get_divisions_by_unit, name="get_divisions_by_unit"),
    path("departments/create/", web_views.create_department, name="department_create"),
    path("departments/", web_views.department_list, name="department_list"),
    path("departments/<int:department_id>/toggle/", web_views.toggle_department_status, name="toggle_department_status"),
    path("section/create/", web_views.create_section, name="section_create"),
    path("section/list/", web_views.section_list, name="section_list"),
    path("section/toggle-status/<int:section_id>/", web_views.toggle_section_status, name="toggle_section_status"),
     path('ajax/units-by-group/', web_views.get_units_by_group, name='get_units_by_group'),
    path('ajax/departments-by-division/', web_views.get_departments_by_division, name='ajax_departments_by_division'),
]
