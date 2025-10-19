from django.contrib import admin
from apps.recruitment.models import JobPosting, Candidate

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['job_code', 'title', 'department', 'designation', 
                    'vacancies', 'deadline', 'status']
    list_filter = ['status', 'department', 'employment_type']
    search_fields = ['job_code', 'title']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'job_posting', 
                    'status', 'applied_date']
    list_filter = ['status', 'applied_date', 'job_posting']
    search_fields = ['first_name', 'last_name', 'email']