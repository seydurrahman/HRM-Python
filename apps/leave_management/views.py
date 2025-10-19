from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework import serializers  # Add this import
from django.db.models import Sum, Q
from django.db import models
from .models import LeaveType, LeaveBalance, LeaveRequest
from .serializers import (
    LeaveTypeSerializer, LeaveBalanceSerializer, 
    LeaveRequestSerializer, LeaveApprovalSerializer
)
from apps.employees.models import Employee

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.filter(is_active=True)
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'leave_type', 'year']
    
    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Get logged-in employee's leave balance"""
        try:
            employee = request.user.employee_profile
            year = request.query_params.get('year', timezone.now().year)
            balances = LeaveBalance.objects.filter(employee=employee, year=year)
            serializer = self.get_serializer(balances, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related(
        'employee', 'leave_type', 'approved_by'
    ).all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'leave_type', 'status']
    
    def perform_create(self, serializer):
        """Automatically set employee from logged-in user"""
        try:
            employee = self.request.user.employee_profile
            serializer.save(employee=employee)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee profile not found")
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get logged-in employee's leave requests"""
        try:
            employee = request.user.employee_profile
            requests = LeaveRequest.objects.filter(employee=employee)
            serializer = self.get_serializer(requests, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get pending leave requests for approval"""
        try:
            employee = request.user.employee_profile
            # Get subordinates' pending requests
            pending = LeaveRequest.objects.filter(
                employee__reporting_manager=employee,
                status='PENDING'
            )
            serializer = self.get_serializer(pending, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """Approve or reject leave request"""
        leave_request = self.get_object()
        serializer = LeaveApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                employee = request.user.employee_profile
                leave_request.status = serializer.validated_data['status']
                leave_request.approved_by = employee
                leave_request.approval_date = timezone.now()
                
                if serializer.validated_data['status'] == 'REJECTED':
                    leave_request.rejection_reason = serializer.validated_data.get(
                        'rejection_reason', ''
                    )
                elif serializer.validated_data['status'] == 'APPROVED':
                    # Update leave balance
                    balance = LeaveBalance.objects.get(
                        employee=leave_request.employee,
                        leave_type=leave_request.leave_type,
                        year=leave_request.start_date.year
                    )
                    balance.used_days += leave_request.total_days
                    balance.update_remaining()
                
                leave_request.save()
                return Response(LeaveRequestSerializer(leave_request).data)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee profile not found'}, 
                              status=status.HTTP_404_NOT_FOUND)
            except LeaveBalance.DoesNotExist:
                return Response({'error': 'Leave balance not found'}, 
                              status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get leave statistics"""
        employee_id = request.query_params.get('employee')
        year = request.query_params.get('year', timezone.now().year)
        
        filters = Q(start_date__year=year)
        if employee_id:
            filters &= Q(employee_id=employee_id)
        
        stats = LeaveRequest.objects.filter(filters).aggregate(
            total_requests=models.Count('id'),
            approved=models.Count('id', filter=Q(status='APPROVED')),
            rejected=models.Count('id', filter=Q(status='REJECTED')),
            pending=models.Count('id', filter=Q(status='PENDING')),
            total_days=Sum('total_days', filter=Q(status='APPROVED'))
        )
        return Response(stats)