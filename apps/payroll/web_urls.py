from django.urls import path
from . import web_views

app_name = "payroll"

urlpatterns = [
    path("", web_views.payroll_list_view, name="list"),        # /dashboard/payroll/
    path("create/", web_views.payroll_create_view, name="create"),  # /dashboard/payroll/create/
]
