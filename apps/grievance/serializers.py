from rest_framework import serializers
from .models import Grievance, DisciplinaryAction

class GrievanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = Grievance
        fields = '__all__'

class DisciplinaryActionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = DisciplinaryAction
        fields = '__all__'