from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanTypeViewSet, LoanViewSet

router = DefaultRouter()
router.register(r'types', LoanTypeViewSet)
router.register(r'applications', LoanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]