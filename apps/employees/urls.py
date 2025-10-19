from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/employees/', include('apps.employees.urls')),
    
    # Web URLs
    path('employees/', include('apps.employees.web_urls', namespace='employees')),
    
    # Other apps...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)