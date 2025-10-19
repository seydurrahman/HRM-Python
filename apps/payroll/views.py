from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework import serializers  # Add this import
from django.db.models import Sum, Avg, Count, Q
from .models import SalaryStructure, Payroll, Bonus, SalaryAdvance
from .serializers import (
    SalaryStructureSerializer, PayrollSerializer, 
    BonusSerializer, SalaryAdvanceSerializer
)
from apps.employees.models import Employee

class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.select_related('employee').all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'is_active']
    
    @action(detail=False, methods=['get'])
    def my_salary(self, request):
        """Get logged-in employee's current salary structure"""
        try:
            employee = request.user.employee_profile
            salary = SalaryStructure.objects.filter(
                employee=employee, 
                is_active=True
            ).first()
            if salary:
                serializer = self.get_serializer(salary)
                return Response(serializer.data)
            return Response({'error': 'No active salary structure found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('employee', 'salary_structure').all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'month', 'year', 'status']
    
    @action(detail=False, methods=['get'])
    def my_payroll(self, request):
        """Get logged-in employee's payroll records"""
        try:
            employee = request.user.employee_profile
            payrolls = Payroll.objects.filter(employee=employee)
            serializer = self.get_serializer(payrolls, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve payroll"""
        payroll = self.get_object()
        try:
            employee = request.user.employee_profile
            payroll.status = 'APPROVED'
            payroll.approved_by = employee
            payroll.approved_at = timezone.now()
            payroll.save()
            return Response(self.get_serializer(payroll).data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Mark payroll as paid"""
        payroll = self.get_object()
        if payroll.status != 'APPROVED':
            return Response({'error': 'Payroll must be approved first'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        payroll.status = 'PAID'
        payroll.save()
        return Response(self.get_serializer(payroll).data)
    
    @action(detail=False, methods=['post'])
    def generate_monthly(self, request):
        """Generate monthly payroll for all employees"""
        month = request.data.get('month', timezone.now().month)
        year = request.data.get('year', timezone.now().year)
        
        # Get all active employees
        employees = Employee.objects.filter(is_active=True)
        generated = 0
        errors = []
        
        for employee in employees:
            try:
                # Check if payroll already exists
                if Payroll.objects.filter(employee=employee, month=month, year=year).exists():
                    continue
                
                # Get active salary structure
                salary_structure = SalaryStructure.objects.filter(
                    employee=employee,
                    is_active=True
                ).first()
                
                if not salary_structure:
                    errors.append(f"No salary structure for {employee.employee_id}")
                    continue
                
                # Get attendance data
                from apps.attendance.models import Attendance
                attendances = Attendance.objects.filter(
                    employee=employee,
                    date__month=month,
                    date__year=year
                )
                
                present_days = attendances.filter(status='PRESENT').count()
                absent_days = attendances.filter(status='ABSENT').count()
                leave_days = attendances.filter(status='ON_LEAVE').count()
                total_hours = attendances.aggregate(Sum('total_hours'))['total_hours__sum'] or 0
                overtime_hours = attendances.aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0
                
                # Calculate prorated salary based on attendance
                working_days = present_days + leave_days
                per_day_salary = salary_structure.basic_salary / 30
                basic_salary = per_day_salary * working_days
                
                # Create payroll
                payroll = Payroll.objects.create(
                    employee=employee,
                    salary_structure=salary_structure,
                    month=month,
                    year=year,
                    payment_date=timezone.now().date(),
                    working_days=30,
                    present_days=present_days,
                    absent_days=absent_days,
                    leave_days=leave_days,
                    overtime_hours=overtime_hours,
                    basic_salary=basic_salary,
                    allowances=salary_structure.gross_salary - salary_structure.basic_salary,
                    overtime_pay=0,
                    bonus=0,
                    other_earnings=0,
                    status='DRAFT'
                )
                payroll.calculate_net_salary()
                payroll.save()
                generated += 1
                
            except Exception as e:
                errors.append(f"Error for {employee.employee_id}: {str(e)}")
        
        return Response({
            'generated': generated,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get payroll statistics"""
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)
        
        stats = Payroll.objects.filter(month=month, year=year).aggregate(
            total_employees=Count('id'),
            total_gross=Sum('gross_earnings'),
            total_deductions=Sum('total_deductions'),
            total_net=Sum('net_salary'),
            avg_salary=Avg('net_salary'),
            paid=Count('id', filter=Q(status='PAID'))
        )
        return Response(stats)

class BonusViewSet(viewsets.ModelViewSet):
    queryset = Bonus.objects.select_related('employee', 'approved_by').all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'bonus_type', 'is_paid']
    
    @action(detail=False, methods=['get'])
    def my_bonuses(self, request):
        """Get logged-in employee's bonuses"""
        try:
            employee = request.user.employee_profile
            bonuses = Bonus.objects.filter(employee=employee)
            serializer = self.get_serializer(bonuses, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class SalaryAdvanceViewSet(viewsets.ModelViewSet):
    queryset = SalaryAdvance.objects.select_related('employee', 'approved_by').all()
    serializer_class = SalaryAdvanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'status']
    
    def perform_create(self, serializer):
        """Automatically set employee from logged-in user"""
        try:
            employee = self.request.user.employee_profile
            serializer.save(employee=employee)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee profile not found")
    
    @action(detail=False, methods=['get'])
    def my_advances(self, request):
        """Get logged-in employee's salary advances"""
        try:
            employee = request.user.employee_profile
            advances = SalaryAdvance.objects.filter(employee=employee)
            serializer = self.get_serializer(advances, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """Approve or reject salary advance request"""
        advance = self.get_object()
        action_type = request.data.get('action')  # 'approve' or 'reject'
        
        if action_type not in ['approve', 'reject']:
            return Response({'error': 'Invalid action'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = request.user.employee_profile
            advance.approved_by = employee
            advance.approval_date = timezone.now().date()
            
            if action_type == 'approve':
                advance.status = 'APPROVED'
            else:
                advance.status = 'REJECTED'
            
            advance.save()
            return Response(self.get_serializer(advance).data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)