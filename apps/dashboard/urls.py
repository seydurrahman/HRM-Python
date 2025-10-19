from django.urls import path
from .views import DashboardAPIView, ReportsAPIView

urlpatterns = [
    path('overview/', DashboardAPIView.as_view(), name='dashboard-overview'),
    path('reports/', ReportsAPIView.as_view(), name='dashboard-reports'),
]