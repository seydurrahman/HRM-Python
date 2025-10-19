from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, HolidayViewSet

router = DefaultRouter()
router.register(r'records', AttendanceViewSet, basename='attendance')
router.register(r'holidays', HolidayViewSet)

urlpatterns = [
    path('', include(router.urls)),
]