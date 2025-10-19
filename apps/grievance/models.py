from django.db import models
from django.utils import timezone
from apps.employees.models import Employee

class GrievanceCategory(models.Model):
    """Categories for grievances"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    escalation_level = models.IntegerField(
        default=1,
        help_text="Level at which this grievance should be escalated"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'grievance_categories'
        verbose_name_plural = 'Grievance Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Grievance(models.Model):
    """Employee Grievances/Complaints"""
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('UNDER_REVIEW', 'Under Review'),
        ('INVESTIGATING', 'Investigating'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        ('ESCALATED', 'Escalated'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    # Basic Information
    grievance_id = models.CharField(max_length=50, unique=True, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='grievances'
    )
    category = models.ForeignKey(
        GrievanceCategory,
        on_delete=models.PROTECT,
        related_name='grievances',
        null=True,
        blank=True
    )
    
    # Grievance Details
    subject = models.CharField(max_length=200)
    description = models.TextField()
    against_person = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Name of person the grievance is against (if applicable)"
    )
    incident_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the incident occurred"
    )
    incident_location = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    
    # Classification
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED'
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Keep complainant identity anonymous"
    )
    
    # Dates
    submitted_date = models.DateTimeField(auto_now_add=True)
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    target_resolution_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_grievances'
    )
    assigned_date = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    investigation_summary = models.TextField(blank=True, null=True)
    resolution = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    
    # Satisfaction
    is_satisfied = models.BooleanField(
        null=True,
        blank=True,
        help_text="Is employee satisfied with resolution?"
    )
    satisfaction_comments = models.TextField(blank=True, null=True)
    satisfaction_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Rating from 1-5"
    )
    
    # Documents
    supporting_document = models.FileField(
        upload_to='grievance_documents/',
        null=True,
        blank=True
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grievances'
        ordering = ['-submitted_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['submitted_date']),
        ]
    
    def __str__(self):
        return f"{self.grievance_id} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.grievance_id:
            # Generate unique grievance ID
            from django.utils import timezone
            year = timezone.now().year
            count = Grievance.objects.filter(
                submitted_date__year=year
            ).count() + 1
            self.grievance_id = f"GRV{year}{count:04d}"
        super().save(*args, **kwargs)
    
    @property
    def days_open(self):
        """Calculate days since grievance was submitted"""
        if self.status in ['RESOLVED', 'CLOSED']:
            return 0
        delta = timezone.now() - self.submitted_date
        return delta.days
    
    @property
    def is_overdue(self):
        """Check if grievance is past target resolution date"""
        if self.target_resolution_date and self.status not in ['RESOLVED', 'CLOSED']:
            return timezone.now().date() > self.target_resolution_date
        return False

class GrievanceComment(models.Model):
    """Comments/Updates on grievances"""
    
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    commented_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comment not visible to complainant"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'grievance_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.grievance.grievance_id}"

class DisciplinaryAction(models.Model):
    """Disciplinary Actions taken against employees"""
    
    ACTION_TYPES = [
        ('VERBAL_WARNING', 'Verbal Warning'),
        ('WRITTEN_WARNING', 'Written Warning'),
        ('FINAL_WARNING', 'Final Warning'),
        ('SUSPENSION', 'Suspension'),
        ('DEMOTION', 'Demotion'),
        ('SALARY_DEDUCTION', 'Salary Deduction'),
        ('TERMINATION', 'Termination'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('MINOR', 'Minor'),
        ('MODERATE', 'Moderate'),
        ('MAJOR', 'Major'),
        ('SEVERE', 'Severe'),
    ]
    
    # Basic Information
    action_id = models.CharField(max_length=50, unique=True, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='disciplinary_actions'
    )
    
    # Related Grievance (if applicable)
    related_grievance = models.ForeignKey(
        Grievance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disciplinary_actions'
    )
    
    # Action Details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='MODERATE'
    )
    violation_type = models.CharField(
        max_length=200,
        help_text="Type of policy violation or misconduct"
    )
    reason = models.TextField(help_text="Detailed reason for disciplinary action")
    
    # Dates
    incident_date = models.DateField(help_text="Date of the incident")
    action_date = models.DateField(help_text="Date action was taken")
    effective_date = models.DateField(help_text="Date when action becomes effective")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date for temporary actions (e.g., suspension)"
    )
    
    # Duration (for suspensions, etc.)
    duration_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duration in days for temporary actions"
    )
    
    # Financial Impact
    salary_deduction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Issued By
    issued_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_actions'
    )
    
    # Additional Information
    remarks = models.TextField(blank=True, null=True)
    supporting_document = models.FileField(
        upload_to='disciplinary_documents/',
        null=True,
        blank=True
    )
    
    # Employee Response
    employee_acknowledgment = models.TextField(
        blank=True,
        null=True,
        help_text="Employee's acknowledgment or response"
    )
    acknowledged_date = models.DateField(null=True, blank=True)
    
    # Appeal Information
    is_appealed = models.BooleanField(default=False)
    appeal_notes = models.TextField(blank=True, null=True)
    appeal_outcome = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'disciplinary_actions'
        ordering = ['-action_date']
        indexes = [
            models.Index(fields=['employee', 'action_date']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.action_id} - {self.employee.employee_id} - {self.action_type}"
    
    def save(self, *args, **kwargs):
        if not self.action_id:
            # Generate unique action ID
            year = timezone.now().year
            count = DisciplinaryAction.objects.filter(
                action_date__year=year
            ).count() + 1
            self.action_id = f"DA{year}{count:04d}"
        super().save(*args, **kwargs)

class GrievanceEscalation(models.Model):
    """Track grievance escalations"""
    
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name='escalations'
    )
    escalated_from = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='escalations_made'
    )
    escalated_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='escalations_received'
    )
    reason = models.TextField()
    escalation_level = models.IntegerField(default=1)
    escalated_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'grievance_escalations'
        ordering = ['-escalated_date']
    
    def __str__(self):
        return f"Escalation of {self.grievance.grievance_id}"

class PolicyViolation(models.Model):
    """Track policy violations"""
    
    VIOLATION_TYPES = [
        ('ATTENDANCE', 'Attendance Policy'),
        ('CODE_OF_CONDUCT', 'Code of Conduct'),
        ('HARASSMENT', 'Harassment'),
        ('DISCRIMINATION', 'Discrimination'),
        ('THEFT', 'Theft/Misappropriation'),
        ('INSUBORDINATION', 'Insubordination'),
        ('POOR_PERFORMANCE', 'Poor Performance'),
        ('SAFETY', 'Safety Violation'),
        ('CONFIDENTIALITY', 'Confidentiality Breach'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='policy_violations'
    )
    violation_type = models.CharField(max_length=30, choices=VIOLATION_TYPES)
    description = models.TextField()
    violation_date = models.DateField()
    reported_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_violations'
    )
    reported_date = models.DateTimeField(auto_now_add=True)
    
    # Related actions
    disciplinary_action = models.ForeignKey(
        DisciplinaryAction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='violations'
    )
    
    class Meta:
        db_table = 'policy_violations'
        ordering = ['-violation_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.violation_type}"