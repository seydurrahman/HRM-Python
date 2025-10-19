from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.employees.models import Employee

class ExitType(models.Model):
    """Types of employee exits"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    requires_notice_period = models.BooleanField(default=True)
    standard_notice_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'exit_types'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class EmployeeSettlement(models.Model):
    """Final Settlement for exiting employees"""
    
    STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('PENDING', 'Pending'),
        ('CALCULATED', 'Calculated'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    EXIT_REASON_CHOICES = [
        ('RESIGNATION', 'Resignation'),
        ('RETIREMENT', 'Retirement'),
        ('TERMINATION', 'Termination'),
        ('END_OF_CONTRACT', 'End of Contract'),
        ('MUTUAL_SEPARATION', 'Mutual Separation'),
        ('DEATH', 'Death'),
        ('ABSCONDING', 'Absconding'),
        ('OTHER', 'Other'),
    ]
    
    # Basic Information
    settlement_id = models.CharField(max_length=50, unique=True, editable=False)
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='settlement'
    )
    exit_type = models.ForeignKey(
        ExitType,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    # Exit Details
    exit_reason = models.CharField(
        max_length=30,
        choices=EXIT_REASON_CHOICES,
        default='RESIGNATION'
    )
    exit_reason_details = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed reason for exit"
    )
    resignation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when resignation was submitted"
    )
    last_working_date = models.DateField()
    relieving_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when employee was officially relieved"
    )
    settlement_date = models.DateField()
    
    # Notice Period
    required_notice_days = models.IntegerField(default=30)
    actual_notice_days = models.IntegerField(default=0)
    notice_period_served = models.BooleanField(default=False)
    notice_shortfall_days = models.IntegerField(default=0)
    
    # Salary Components - Payables
    pending_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Salary for days worked in final month"
    )
    leave_encashment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Payment for unused leave days"
    )
    gratuity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Gratuity payment (if applicable)"
    )
    notice_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Payment in lieu of notice period"
    )
    bonus_payable = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Pending bonus or incentives"
    )
    overtime_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Pending overtime payment"
    )
    reimbursements = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Pending reimbursements"
    )
    provident_fund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="PF balance to be transferred"
    )
    other_payments = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Any other payments"
    )
    
    # Deductions
    notice_period_recovery = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Recovery for notice period shortfall"
    )
    loan_recovery = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Outstanding loan amount"
    )
    advance_recovery = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Salary advance recovery"
    )
    asset_recovery = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Cost of unreturned company assets"
    )
    training_bond_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Training bond penalty (if applicable)"
    )
    damage_compensation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Compensation for damages"
    )
    tax_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tax deduction on settlement"
    )
    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Any other deductions"
    )
    
    # Totals
    total_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_deductible = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    net_settlement_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Leave Details
    total_leave_balance = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text="Total unused leave days"
    )
    encashable_leave_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0
    )
    
    # Status and Processing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='INITIATED'
    )
    
    # Approval Workflow
    calculated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calculated_settlements'
    )
    calculated_at = models.DateTimeField(null=True, blank=True)
    
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_settlements'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Payment Details
    payment_mode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Mode of payment (Bank Transfer, Cheque, etc.)"
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Payment transaction reference"
    )
    payment_date = models.DateField(null=True, blank=True)
    
    # Additional Information
    remarks = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes (not visible to employee)"
    )
    
    # Documents
    settlement_letter = models.FileField(
        upload_to='settlement_documents/',
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employee_settlements'
        ordering = ['-settlement_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['settlement_date']),
        ]
    
    def __str__(self):
        return f"{self.settlement_id} - {self.employee.employee_id}"
    
    def save(self, *args, **kwargs):
        if not self.settlement_id:
            # Generate unique settlement ID
            year = timezone.now().year
            count = EmployeeSettlement.objects.filter(
                created_at__year=year
            ).count() + 1
            self.settlement_id = f"STL{year}{count:05d}"
        
        # Auto-calculate notice shortfall
        if self.required_notice_days and self.actual_notice_days:
            self.notice_shortfall_days = max(
                0,
                self.required_notice_days - self.actual_notice_days
            )
            self.notice_period_served = self.notice_shortfall_days == 0
        
        super().save(*args, **kwargs)
    
    def calculate_net_amount(self):
        """Calculate net settlement amount"""
        self.total_payable = (
            self.pending_salary +
            self.leave_encashment +
            self.gratuity +
            self.notice_pay +
            self.bonus_payable +
            self.overtime_pay +
            self.reimbursements +
            self.provident_fund_amount +
            self.other_payments
        )
        
        self.total_deductible = (
            self.notice_period_recovery +
            self.loan_recovery +
            self.advance_recovery +
            self.asset_recovery +
            self.training_bond_penalty +
            self.damage_compensation +
            self.tax_deduction +
            self.other_deductions
        )
        
        self.net_settlement_amount = self.total_payable - self.total_deductible
        self.save()
        return self.net_settlement_amount
    
    def calculate_leave_encashment(self, per_day_salary):
        """Calculate leave encashment amount"""
        self.leave_encashment = float(self.encashable_leave_days) * float(per_day_salary)
        return self.leave_encashment
    
    def calculate_gratuity(self, years_of_service, last_salary):
        """Calculate gratuity (15 days salary for each year of service)"""
        if years_of_service >= 5:  # Gratuity applicable after 5 years
            self.gratuity = (float(last_salary) * 15 * years_of_service) / 26
        else:
            self.gratuity = 0
        return self.gratuity
    
    def calculate_notice_recovery(self, per_day_salary):
        """Calculate notice period recovery"""
        if self.notice_shortfall_days > 0:
            self.notice_period_recovery = self.notice_shortfall_days * float(per_day_salary)
        return self.notice_period_recovery

class ExitInterview(models.Model):
    """Exit Interview Details"""
    
    settlement = models.OneToOneField(
        EmployeeSettlement,
        on_delete=models.CASCADE,
        related_name='exit_interview'
    )
    interview_date = models.DateField()
    interviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_exit_interviews'
    )
    
    # Feedback Questions
    reason_for_leaving = models.TextField()
    job_satisfaction_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Rating from 1-10"
    )
    work_environment_rating = models.IntegerField(null=True, blank=True)
    management_rating = models.IntegerField(null=True, blank=True)
    career_growth_rating = models.IntegerField(null=True, blank=True)
    compensation_rating = models.IntegerField(null=True, blank=True)
    
    would_recommend_company = models.BooleanField(
        null=True,
        blank=True,
        help_text="Would recommend company to others?"
    )
    would_consider_rejoining = models.BooleanField(
        null=True,
        blank=True,
        help_text="Would consider rejoining in future?"
    )
    
    positive_aspects = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exit_interviews'
    
    def __str__(self):
        return f"Exit Interview - {self.settlement.employee.employee_id}"

class AssetReturn(models.Model):
    """Track return of company assets"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RETURNED', 'Returned'),
        ('DAMAGED', 'Damaged'),
        ('LOST', 'Lost'),
        ('NOT_APPLICABLE', 'Not Applicable'),
    ]
    
    settlement = models.ForeignKey(
        EmployeeSettlement,
        on_delete=models.CASCADE,
        related_name='asset_returns'
    )
    asset_name = models.CharField(max_length=200)
    asset_code = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    issued_date = models.DateField(null=True, blank=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    condition = models.TextField(blank=True, help_text="Condition of returned asset")
    recovery_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Recovery amount if damaged/lost"
    )
    verified_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_asset_returns'
    )
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'asset_returns'
        ordering = ['expected_return_date']
    
    def __str__(self):
        return f"{self.asset_name} - {self.settlement.employee.employee_id}"

class ClearanceChecklist(models.Model):
    """Departmental clearance checklist"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLEARED', 'Cleared'),
        ('ON_HOLD', 'On Hold'),
    ]
    
    settlement = models.ForeignKey(
        EmployeeSettlement,
        on_delete=models.CASCADE,
        related_name='clearances'
    )
    department_name = models.CharField(max_length=100)
    clearance_item = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    cleared_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clearances_given'
    )
    cleared_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clearance_checklists'
        ordering = ['department_name']
    
    def __str__(self):
        return f"{self.department_name} - {self.clearance_item}"

class SettlementDocument(models.Model):
    """Documents related to settlement"""
    
    DOCUMENT_TYPES = [
        ('RESIGNATION_LETTER', 'Resignation Letter'),
        ('RELIEVING_LETTER', 'Relieving Letter'),
        ('EXPERIENCE_CERTIFICATE', 'Experience Certificate'),
        ('NOC', 'No Objection Certificate'),
        ('FORM_16', 'Form 16'),
        ('SETTLEMENT_LETTER', 'Settlement Letter'),
        ('OTHER', 'Other'),
    ]
    
    settlement = models.ForeignKey(
        EmployeeSettlement,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='settlement_documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'settlement_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.document_type} - {self.settlement.settlement_id}"