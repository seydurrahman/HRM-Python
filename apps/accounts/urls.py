# apps/accounts/urls.py   (API)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .import views
from .views import (
    UserViewSet, DepartmentViewSet, DesignationViewSet,units_by_group,
    api_register_view, api_login_view, api_logout_view, api_profile_view, api_update_profile_view,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'designations', DesignationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', api_register_view, name='api-register'),
    path('login/', api_login_view, name='api-login'),
    path('logout/', api_logout_view, name='api-logout'),
    path('profile/', api_profile_view, name='api-profile'),
    path('profile/update/', api_update_profile_view, name='api-profile-update'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('accounts.urls')),
    path('api/ajax/units-by-group/<int:group_id>/', views.units_by_group, name='ajax-units-by-group'),
]


