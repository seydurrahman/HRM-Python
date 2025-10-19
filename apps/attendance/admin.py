from django.contrib import admin
from .models import Attendance, Holiday

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 
                    'total_hours', 'overtime_hours']
    list_filter = ['status', 'date', 'is_manual_entry']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 
                     'employee__user__last_name']
    date_hierarchy = 'date'
    readonly_fields = ['total_hours', 'overtime_hours']
    
    def save_model(self, request, obj, form, change):
        if obj.check_in and obj.check_out:
            obj.calculate_hours()
        super().save_model(request, obj, form, change)

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'is_optional']
    list_filter = ['is_optional', 'date']
    search_fields = ['name']
    date_hierarchy = 'date'