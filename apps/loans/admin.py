from django.contrib import admin
from apps.loans.models import LoanType, Loan

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_amount', 'interest_rate', 'max_tenure_months', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['employee', 'loan_type', 'loan_amount', 'status', 
                    'paid_amount', 'remaining_amount']
    list_filter = ['status', 'loan_type']
    search_fields = ['employee__employee_id', 'employee__user__first_name']