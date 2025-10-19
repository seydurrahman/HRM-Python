from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalaryStructureViewSet, PayrollViewSet, 
    BonusViewSet, SalaryAdvanceViewSet
)

router = DefaultRouter()
router.register(r'salary-structure', SalaryStructureViewSet)
router.register(r'payroll', PayrollViewSet)
router.register(r'bonuses', BonusViewSet)
router.register(r'advances', SalaryAdvanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]