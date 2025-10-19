from django.db import models
from apps.employees.models import Employee

class DocumentCategory(models.Model):
    """Document Categories for organizing employee documents"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    requires_expiry = models.BooleanField(
        default=False,
        help_text="Does this document type have an expiry date?"
    )
    is_mandatory = models.BooleanField(
        default=False,
        help_text="Is this document mandatory for all employees?"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_categories'
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Document(models.Model):
    """Employee Documents Storage"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('PENDING_VERIFICATION', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name='documents'
    )
    
    # Document Information
    title = models.CharField(max_length=200)
    document_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Document ID/Reference Number (e.g., Passport Number, License Number)"
    )
    document_file = models.FileField(
        upload_to='employee_documents/%Y/%m/',
        help_text="Upload PDF, DOC, or Image files"
    )
    file_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    file_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Dates
    issue_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when document was issued"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date of the document"
    )
    
    # Additional Information
    description = models.TextField(blank=True, null=True)
    issuing_authority = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Organization/Authority that issued the document"
    )
    
    # Status and Verification
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING_VERIFICATION'
    )
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Upload Information
    uploaded_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    is_confidential = models.BooleanField(
        default=False,
        help_text="Mark as confidential (restricted access)"
    )
    version = models.IntegerField(
        default=1,
        help_text="Document version number"
    )
    replaced_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replaces'
    )
    
    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['employee', 'category']),
            models.Index(fields=['status']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Auto-set file size and type
        if self.document_file:
            self.file_size = self.document_file.size
            self.file_type = self.document_file.name.split('.')[-1].upper()
        
        # Check if document is expired
        if self.expiry_date:
            from django.utils import timezone
            if self.expiry_date < timezone.now().date() and self.status == 'ACTIVE':
                self.status = 'EXPIRED'
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            from django.utils import timezone
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

class DocumentTemplate(models.Model):
    """Templates for standard documents (offer letters, NDAs, etc.)"""
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.CASCADE,
        related_name='templates'
    )
    description = models.TextField(blank=True)
    template_file = models.FileField(upload_to='document_templates/')
    
    # Template variables (JSON format)
    # e.g., {"employee_name": "Employee Name", "salary": "Salary Amount"}
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template variables in JSON format"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DocumentAccessLog(models.Model):
    """Track document access for audit purposes"""
    
    ACTION_CHOICES = [
        ('VIEW', 'Viewed'),
        ('DOWNLOAD', 'Downloaded'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VERIFY', 'Verified'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    accessed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'document_access_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.document.title} by {self.accessed_by}"

class DocumentRequest(models.Model):
    """Employee requests for specific documents"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='document_requests'
    )
    document_category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.CASCADE
    )
    request_type = models.CharField(
        max_length=100,
        help_text="Type of document requested (e.g., Experience Letter, Salary Certificate)"
    )
    purpose = models.TextField(help_text="Purpose of the document request")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Processing
    requested_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_document_requests'
    )
    processed_date = models.DateTimeField(null=True, blank=True)
    processing_notes = models.TextField(blank=True, null=True)
    
    # Generated document
    generated_document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='request'
    )
    
    class Meta:
        db_table = 'document_requests'
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.request_type}"

class DocumentReminder(models.Model):
    """Automated reminders for document expiry"""
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_date = models.DateField()
    days_before_expiry = models.IntegerField(
        help_text="Number of days before expiry to send reminder"
    )
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    recipient_email = models.EmailField()
    
    class Meta:
        db_table = 'document_reminders'
        ordering = ['reminder_date']
    
    def __str__(self):
        return f"Reminder for {self.document.title} - {self.reminder_date}"