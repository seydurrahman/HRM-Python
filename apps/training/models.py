from django.db import models
from apps.accounts.models import Department, Designation
from apps.employees.models import Employee

class TrainingProgram(models.Model):
    """Training Programs"""
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    trainer_name = models.CharField(max_length=100)
    duration_hours = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=20)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'training_programs'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class TrainingParticipant(models.Model):
    """Training Participants"""
    
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
        ('FAILED', 'Failed'),
    ]
    
    training_program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='participants')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='trainings')
    enrollment_date = models.DateField(auto_now_add=True)
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    certificate = models.FileField(upload_to='training_certificates/', null=True, blank=True)
    
    class Meta:
        db_table = 'training_participants'
        unique_together = ['training_program', 'employee']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.training_program.name}"