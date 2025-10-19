from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ API Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # ✅ API Endpoints
    # path("api/accounts/", include("apps.accounts.api_urls")),
    # path("api/employees/", include("apps.employees.api_urls")),
    # path("api/attendance/", include("apps.attendance.api_urls")),
    # path("api/leave/", include("apps.leave_management.api_urls")),
    # path("api/payroll/", include("apps.payroll.api_urls")),
    # path("api/recruitment/", include("apps.recruitment.api_urls")),
    # path("api/training/", include("apps.training.api_urls")),
    # path("api/performance/", include("apps.performance.api_urls")),
    # path("api/loans/", include("apps.loans.api_urls")),
    # path("api/provident-fund/", include("apps.provident_fund.api_urls")),
    # path("api/documents/", include("apps.documents.api_urls")),
    # path("api/grievance/", include("apps.grievance.api_urls")),
    # path("api/settlement/", include("apps.settlement.api_urls")),
    # path("api/dashboard/", include("apps.dashboard.api_urls")),

    # Web routes (for HTML login/register)
    path("accounts/", include(("apps.accounts.web_urls", "accounts"), namespace="accounts")),
    path("employees/", include(("apps.employees.web_urls", "employees"), namespace="employees")),
    path("attendance/", include(("apps.attendance.web_urls", "attendance"), namespace="attendance")),
    path("leave/", include(("apps.leave_management.web_urls", "leave"), namespace="leave")),
    path("payroll/", include(("apps.payroll.web_urls", "payroll"), namespace="payroll")),
    path("recruitment/", include(("apps.recruitment.web_urls", "recruitment"), namespace="recruitment")),
    path("training/", include(("apps.training.web_urls", "training"), namespace="training")),
    path("performance/", include(("apps.performance.web_urls", "performance"), namespace="performance")),
    path("loans/", include(("apps.loans.web_urls", "loans"), namespace="loans")),
    path("provident-fund/", include(("apps.provident_fund.web_urls", "provident_fund"), namespace="provident_fund")),
    path("documents/", include(("apps.documents.web_urls", "documents"), namespace="documents")),
    path("grievance/", include(("apps.grievance.web_urls", "grievance"), namespace="grievance")),
    path("settlement/", include(("apps.settlement.web_urls", "settlement"), namespace="settlement")),



    # ✅ Django web views
    path("", include("apps.dashboard.web_urls")),
]

# ✅ Static & Media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ Custom Admin Branding
admin.site.site_header = "HRM System Administration"
admin.site.site_title = "HRM Admin Portal"
admin.site.index_title = "Welcome to HRM System Administration"
