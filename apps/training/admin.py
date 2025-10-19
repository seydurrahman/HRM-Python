from django.contrib import admin
from apps.training.models import TrainingProgram, TrainingParticipant

@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'trainer_name', 'start_date', 'end_date', 
                    'duration_hours', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['code', 'name', 'trainer_name']

@admin.register(TrainingParticipant)
class TrainingParticipantAdmin(admin.ModelAdmin):
    list_display = ['employee', 'training_program', 'status', 'score', 'completion_date']
    list_filter = ['status', 'training_program']
    search_fields = ['employee__employee_id', 'employee__user__first_name']