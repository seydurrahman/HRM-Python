from django.contrib import admin
from apps.settlement.models import EmployeeSettlement

@admin.register(EmployeeSettlement)
class EmployeeSettlementAdmin(admin.ModelAdmin):
    list_display = ['employee', 'last_working_date', 'settlement_date', 
                    'net_settlement_amount', 'status']
    list_filter = ['status', 'settlement_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name']
    readonly_fields = ['total_payable', 'total_deductible', 'net_settlement_amount']
    
    def save_model(self, request, obj, form, change):
        obj.calculate_net_amount()
        super().save_model(request, obj, form, change)
