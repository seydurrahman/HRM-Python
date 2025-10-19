from rest_framework import serializers
from .models import EmployeeSettlement

class EmployeeSettlementSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeSettlement
        fields = '__all__'
        read_only_fields = ['total_payable', 'total_deductible', 'net_settlement_amount']