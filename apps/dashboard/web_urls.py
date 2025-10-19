from django.urls import path
from .web_views import home_view, dashboard_view, admin_dashboard_view, employee_dashboard_view

app_name = 'dashboard'

urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/admin/', admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/employee/', employee_dashboard_view, name='employee_dashboard'),
]