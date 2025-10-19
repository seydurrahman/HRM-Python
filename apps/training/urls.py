from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingProgramViewSet, TrainingParticipantViewSet

router = DefaultRouter()
router.register(r'programs', TrainingProgramViewSet)
router.register(r'participants', TrainingParticipantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]