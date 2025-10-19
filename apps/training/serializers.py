from rest_framework import serializers
from .models import TrainingProgram, TrainingParticipant

class TrainingProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProgram
        fields = '__all__'

class TrainingParticipantSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    program_name = serializers.CharField(source='training_program.name', read_only=True)
    
    class Meta:
        model = TrainingParticipant
        fields = '__all__'