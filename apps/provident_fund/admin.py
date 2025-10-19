from django.contrib import admin
from apps.provident_fund.models import ProvidentFund

@admin.register(ProvidentFund)
class ProvidentFundAdmin(admin.ModelAdmin):
    list_display = ['employee', 'employee_contribution_percent', 
                    'employer_contribution_percent', 'total_balance', 'is_active']
    list_filter = ['is_active']
    search_fields = ['employee__employee_id', 'employee__user__first_name']