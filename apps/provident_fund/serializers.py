from rest_framework import serializers
from .models import ProvidentFund

class ProvidentFundSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = ProvidentFund
        fields = '__all__'