from rest_framework import serializers
from .models import LoanType, Loan

class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    loan_type_name = serializers.CharField(source='loan_type.name', read_only=True)
    
    class Meta:
        model = Loan
        fields = '__all__'