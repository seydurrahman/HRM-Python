from django.db import models
from django.utils import timezone
from apps.employees.models import Employee

class LeaveType(models.Model):
    """Types of Leave"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    days_allowed = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=True)
    requires_document = models.BooleanField(default=False)
    carry_forward = models.BooleanField(default=False)
    max_carry_forward_days = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'leave_types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.days_allowed} days)"

class LeaveBalance(models.Model):
    """Employee Leave Balance"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    remaining_days = models.DecimalField(max_digits=5, decimal_places=1)
    carry_forward_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} - {self.year}"
    
    def update_remaining(self):
        """Update remaining days"""
        self.remaining_days = self.total_days - self.used_days
        self.save()

class LeaveRequest(models.Model):
    """Leave Applications"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Supporting documents
    supporting_document = models.FileField(upload_to='leave_documents/', null=True, blank=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} - {self.start_date}"
    
    def calculate_days(self):
        """Calculate total leave days excluding weekends"""
        from datetime import timedelta
        days = 0
        current = self.start_date
        while current <= self.end_date:
            if current.weekday() < 5:  # Monday to Friday
                days += 1
            current += timedelta(days=1)
        self.total_days = days
        return days