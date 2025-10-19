from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Department, Designation

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def validate_email(self, value):
        if self.instance and User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def update(self, instance, validated_data):
        # Don't allow role changes through normal update
        if 'role' in validated_data and not self.context['request'].user.is_admin:
            validated_data.pop('role')
        return super().update(instance, validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'role', 'phone', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'username': {'required': False},
            'role': {'default': 'EMPLOYEE'}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    sub_department_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'head', 'head_name',
            'parent_department', 'budget', 'is_active', 'employee_count',
            'sub_department_count', 'created_at', 'updated_at'
        ]
    
    def get_employee_count(self, obj):
        return obj.employees.count()
    
    def get_sub_department_count(self, obj):
        return obj.sub_departments.count()

class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Designation
        fields = [
            'id', 'title', 'code', 'department', 'department_name',
            'level', 'description', 'responsibilities', 'min_salary',
            'max_salary', 'is_active', 'employee_count', 'created_at', 'updated_at'
        ]
    
    def get_employee_count(self, obj):
        return obj.employees.count()