from django.db import models
from apps.accounts.models import Department, Designation
from apps.employees.models import Employee
class PerformanceReview(models.Model):
    """Employee Performance Reviews"""
    
    REVIEW_TYPES = [
        ('PROBATION', 'Probation Review'),
        ('QUARTERLY', 'Quarterly Review'),
        ('HALF_YEARLY', 'Half Yearly Review'),
        ('ANNUAL', 'Annual Review'),
    ]
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='conducted_reviews')
    
    # Ratings
    quality_of_work = models.IntegerField(choices=RATING_CHOICES)
    productivity = models.IntegerField(choices=RATING_CHOICES)
    communication = models.IntegerField(choices=RATING_CHOICES)
    teamwork = models.IntegerField(choices=RATING_CHOICES)
    initiative = models.IntegerField(choices=RATING_CHOICES)
    punctuality = models.IntegerField(choices=RATING_CHOICES)
    
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2)
    strengths = models.TextField()
    areas_of_improvement = models.TextField()
    goals_for_next_period = models.TextField()
    comments = models.TextField(blank=True)
    
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_reviews'
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.review_type} - {self.review_date}"
    
    def calculate_overall_rating(self):
        """Calculate overall rating"""
        total = (
            self.quality_of_work + 
            self.productivity + 
            self.communication + 
            self.teamwork + 
            self.initiative + 
            self.punctuality
        )
        self.overall_rating = round(total / 6, 2)
        return self.overall_rating