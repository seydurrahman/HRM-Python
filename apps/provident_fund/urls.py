from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvidentFundViewSet

router = DefaultRouter()
router.register(r'', ProvidentFundViewSet)

urlpatterns = [
    path('', include(router.urls)),
]