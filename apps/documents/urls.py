from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentCategoryViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'categories', DocumentCategoryViewSet)
router.register(r'files', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]