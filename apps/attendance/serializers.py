from rest_framework import serializers
from .models import Attendance, Holiday

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['total_hours', 'overtime_hours']
    
    def create(self, validated_data):
        attendance = super().create(validated_data)
        if attendance.check_in and attendance.check_out:
            attendance.calculate_hours()
            attendance.save()
        return attendance

class CheckInSerializer(serializers.Serializer):
    location = serializers.CharField(required=False, allow_blank=True)

class CheckOutSerializer(serializers.Serializer):
    location = serializers.CharField(required=False, allow_blank=True)

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'