from django.db import models
from apps.accounts.models import Department, Designation
from apps.employees.models import Employee
# Create your models here.


class ProvidentFund(models.Model):
    """Employee Provident Fund"""
    
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='provident_fund')
    employee_contribution_percent = models.DecimalField(max_digits=5, decimal_places=2)
    employer_contribution_percent = models.DecimalField(max_digits=5, decimal_places=2)
    total_employee_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_employer_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)