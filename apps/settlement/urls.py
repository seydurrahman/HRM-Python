from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeSettlementViewSet

router = DefaultRouter()
router.register(r'', EmployeeSettlementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]