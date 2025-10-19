from django.contrib import admin
from apps.documents.models import DocumentCategory, Document

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'category', 'title', 'issue_date', 
                    'expiry_date', 'uploaded_at']
    list_filter = ['category', 'uploaded_at']
    search_fields = ['employee__employee_id', 'title']