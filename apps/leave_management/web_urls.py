from django.urls import path
from . import web_views

app_name = "leave_management"

urlpatterns = [
    path("", web_views.leave_list_view, name="list"),       # /dashboard/leave/
    path("create/", web_views.leave_create_view, name="create"),  # /dashboard/leave/create/
]
