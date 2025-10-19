from django.contrib import admin
from apps.performance.models import PerformanceReview

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'review_type', 'review_date', 'overall_rating', 'reviewer']
    list_filter = ['review_type', 'review_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']
    readonly_fields = ['overall_rating']
    
    def save_model(self, request, obj, form, change):
        obj.calculate_overall_rating()
        super().save_model(request, obj, form, change)