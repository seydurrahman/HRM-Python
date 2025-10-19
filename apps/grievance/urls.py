from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GrievanceViewSet, DisciplinaryActionViewSet

router = DefaultRouter()
router.register(r'complaints', GrievanceViewSet)
router.register(r'disciplinary-actions', DisciplinaryActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]