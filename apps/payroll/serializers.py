from rest_framework import serializers
from .models import SalaryStructure, Payroll, Bonus, SalaryAdvance

class SalaryStructureSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = SalaryStructure
        fields = '__all__'
        read_only_fields = ['gross_salary']
    
    def create(self, validated_data):
        salary = super().create(validated_data)
        salary.calculate_gross()
        salary.save()
        return salary

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True)
    
    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['gross_earnings', 'total_deductions', 'net_salary']
    
    def create(self, validated_data):
        payroll = super().create(validated_data)
        payroll.calculate_net_salary()
        payroll.save()
        return payroll

class BonusSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = Bonus
        fields = '__all__'

class SalaryAdvanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = SalaryAdvance
        fields = '__all__'
        read_only_fields = ['installment_amount', 'recovered_amount']
    
    def create(self, validated_data):
        advance = super().create(validated_data)
        advance.calculate_installment()
        advance.save()
        return advance