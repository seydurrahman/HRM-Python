from django.contrib import admin
from .models import SalaryStructure, Payroll, Bonus, SalaryAdvance

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['employee', 'effective_date', 'basic_salary', 'gross_salary', 'is_active']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']
    readonly_fields = ['gross_salary']
    
    def save_model(self, request, obj, form, change):
        obj.calculate_gross()
        super().save_model(request, obj, form, change)

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'gross_earnings', 
                    'total_deductions', 'net_salary', 'status']
    list_filter = ['status', 'year', 'month']
    search_fields = ['employee__employee_id', 'employee__user__first_name']
    readonly_fields = ['gross_earnings', 'total_deductions', 'net_salary']
    
    actions = ['approve_payrolls', 'mark_as_paid']
    
    def approve_payrolls(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, f"{queryset.count()} payrolls approved")
    approve_payrolls.short_description = "Approve selected payrolls"
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='PAID')
        self.message_user(request, f"{queryset.count()} payrolls marked as paid")
    mark_as_paid.short_description = "Mark as paid"

@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ['employee', 'bonus_type', 'amount', 'payment_date', 'is_paid']
    list_filter = ['bonus_type', 'is_paid', 'payment_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']

@admin.register(SalaryAdvance)
class SalaryAdvanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'amount', 'request_date', 'status', 
                    'installments', 'recovered_amount']
    list_filter = ['status', 'request_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']
    readonly_fields = ['installment_amount', 'recovered_amount']