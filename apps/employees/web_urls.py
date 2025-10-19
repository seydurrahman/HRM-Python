from django.urls import path
from . import web_views

app_name = 'employees'

urlpatterns = [
    path("", web_views.employee_list_view, name="list"),
    path("create/", web_views.employee_create_view, name="create"),
    path("update/<int:pk>/", web_views.employee_update_view, name="update"),
    path("delete/<int:pk>/", web_views.employee_delete_view, name="delete"),
]