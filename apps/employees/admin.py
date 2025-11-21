from django.contrib import admin
from .models import Employee, EducationRecord, Dependent

class EducationRecordInline(admin.TabularInline):
    model = EducationRecord
    extra = 1

# class WorkExperienceInline(admin.TabularInline):
#     model = WorkExperience
#     extra = 1

class DependentInline(admin.TabularInline):
    model = Dependent
    extra = 1

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'designation', 
                    'employment_type', 'date_of_joining', 'is_active']
    list_filter = ['department', 'designation', 'employment_type', 'is_active', 
                   'date_of_joining']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 
                     'user__email', 'mobile_number']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    inlines = [EducationRecordInline, DependentInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id', 'photo')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'marital_status', 'blood_group', 'nationality')
        }),
        ('Contact Information', {
            'fields': ('personal_email', 'mobile_number', 'emergency_contact_name', 
                      'emergency_contact_number', 'emergency_contact_relation')
        }),
        ('Address', {
            'fields': ('postal_code', 'country')
        }),
        ('Employment Details', {
            'fields': ('department', 'designation', 'employment_type', 'date_of_joining', 
                      'date_of_confirmation', 'probation_period_months', 'reporting_manager')
        }),
        ('Documents', {
            'fields': ('passport_number', 'tin_number')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'bank_account_number', 'bank_branch')
        }),
        ('Status', {
            'fields': ('is_active', 'resignation_date', 'termination_date', 'exit_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'