from django.urls import path
from . import web_views

app_name = 'employees'

urlpatterns = [
    path("", web_views.employee_list_view, name="list"),
    path("create/", web_views.employee_create_view, name="create"),
    path("update/<int:pk>/", web_views.employee_update_view, name="update"),
    path("delete/<int:pk>/", web_views.employee_delete_view, name="delete"),
    # AJAX paths
    path('ajax/load-divisions/', web_views.ajax_load_divisions, name='ajax_load_divisions'),
    path('ajax/load-departments/', web_views.ajax_load_departments, name='ajax_load_departments'),
    path('ajax/load-sections/', web_views.ajax_load_sections, name='ajax_load_sections'),
    path('ajax/load-sub-sections/', web_views.ajax_load_sub_sections, name='ajax_load_sub_sections'),
    path('ajax/load-floors/', web_views.ajax_load_floors, name='ajax_load_floors'),
    path('ajax/load-lines/', web_views.ajax_load_lines, name='ajax_load_lines'),
]

