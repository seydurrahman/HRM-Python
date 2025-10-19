from django.urls import path
from . import web_views  # create this if not exists

app_name = "attendance"

urlpatterns = [
    path("", web_views.attendance_list_view, name="list"),
    path("create/", web_views.attendance_create_view, name="create"),
]
