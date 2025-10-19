from django.contrib import admin
from apps.grievance.models import Grievance, DisciplinaryAction

@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'subject', 'category', 'priority', 
                    'status', 'submitted_date']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['employee__employee_id', 'subject']

@admin.register(DisciplinaryAction)
class DisciplinaryActionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'action_type', 'action_date', 'issued_by']
    list_filter = ['action_type', 'action_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']