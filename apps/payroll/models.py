from django.db import models
from django.core.validators import MinValueValidator
from apps.employees.models import Employee

class SalaryStructure(models.Model):
    """Employee Salary Structure"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_structures')
    effective_date = models.DateField()
    
    # Basic Components
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    house_rent_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Other Allowances
    food_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mobile_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Gross Salary
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'salary_structures'
        ordering = ['-effective_date']
        unique_together = ['employee', 'effective_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.gross_salary}"
    
    def calculate_gross(self):
        """Calculate gross salary"""
        self.gross_salary = (
            self.basic_salary + 
            self.house_rent_allowance + 
            self.medical_allowance + 
            self.transport_allowance + 
            self.special_allowance + 
            self.food_allowance + 
            self.mobile_allowance + 
            self.other_allowances
        )
        return self.gross_salary

class Payroll(models.Model):
    """Monthly Payroll Records"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROCESSED', 'Processed'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.PROTECT)
    
    # Period
    month = models.IntegerField(validators=[MinValueValidator(1)])
    year = models.IntegerField()
    payment_date = models.DateField()
    
    # Attendance based
    working_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    leave_days = models.IntegerField(default=0)
    holidays = models.IntegerField(default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Earnings
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Deductions
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    absent_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Net Salary
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    remarks = models.TextField(blank=True, null=True)
    
    # Approval
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payrolls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payrolls'
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['employee', 'year', 'month']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.month}/{self.year}"
    
    def calculate_net_salary(self):
        """Calculate net salary"""
        self.gross_earnings = (
            self.basic_salary + 
            self.allowances + 
            self.overtime_pay + 
            self.bonus + 
            self.other_earnings
        )
        
        self.total_deductions = (
            self.tax_deduction + 
            self.provident_fund + 
            self.loan_deduction + 
            self.advance_deduction + 
            self.absent_deduction + 
            self.other_deductions
        )
        
        self.net_salary = self.gross_earnings - self.total_deductions
        return self.net_salary

class Bonus(models.Model):
    """Employee Bonuses"""
    
    BONUS_TYPES = [
        ('PERFORMANCE', 'Performance Bonus'),
        ('FESTIVAL', 'Festival Bonus'),
        ('ANNUAL', 'Annual Bonus'),
        ('PROJECT', 'Project Completion'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bonuses')
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()
    reason = models.TextField()
    payment_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_bonuses'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bonuses'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.bonus_type} - {self.amount}"

class SalaryAdvance(models.Model):
    """Salary Advance Requests"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
        ('RECOVERED', 'Recovered'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_advances')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    request_date = models.DateField(auto_now_add=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Recovery
    installments = models.IntegerField(default=1)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recovered_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_advances'
    )
    approval_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'salary_advances'
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.amount}"
    
    def calculate_installment(self):
        """Calculate monthly installment"""
        if self.installments > 0:
            self.installment_amount = self.amount / self.installments
        return self.installment_amount