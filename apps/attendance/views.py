from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from . models import Attendance, Holiday,Employee
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .models import Attendance, Holiday
from .serializers import (
    AttendanceSerializer, CheckInSerializer, CheckOutSerializer, HolidaySerializer
)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'date', 'status']
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Employee check-in"""
        try:
            employee = request.user.employee_profile
            today = timezone.now().date()
            
            # Check if already checked in
            if Attendance.objects.filter(employee=employee, date=today).exists():
                return Response({'error': 'Already checked in today'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CheckInSerializer(data=request.data)
            if serializer.is_valid():
                attendance = Attendance.objects.create(
                    employee=employee,
                    date=today,
                    check_in=timezone.now(),
                    check_in_location=serializer.validated_data.get('location', ''),
                    status='PRESENT'
                )
                return Response(AttendanceSerializer(attendance).data, 
                              status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Employee check-out"""
        try:
            employee = request.user.employee_profile
            today = timezone.now().date()
            
            attendance = Attendance.objects.filter(
                employee=employee, 
                date=today, 
                check_out__isnull=True
            ).first()
            
            if not attendance:
                return Response({'error': 'No check-in found for today'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CheckOutSerializer(data=request.data)
            if serializer.is_valid():
                attendance.check_out = timezone.now()
                attendance.check_out_location = serializer.validated_data.get('location', '')
                attendance.calculate_hours()
                attendance.save()
                return Response(AttendanceSerializer(attendance).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Get logged-in employee's attendance"""
        try:
            employee = request.user.employee_profile
            month = request.query_params.get('month', timezone.now().month)
            year = request.query_params.get('year', timezone.now().year)
            
            attendances = Attendance.objects.filter(
                employee=employee,
                date__month=month,
                date__year=year
            )
            serializer = self.get_serializer(attendances, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get attendance summary"""
        employee_id = request.query_params.get('employee')
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)
        
        filters = Q(date__month=month, date__year=year)
        if employee_id:
            filters &= Q(employee_id=employee_id)
        
        summary = Attendance.objects.filter(filters).aggregate(
            total_days=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            leave=Count('id', filter=Q(status='ON_LEAVE')),
            total_hours=Sum('total_hours'),
            overtime_hours=Sum('overtime_hours')
        )
        return Response(summary)

class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming holidays"""
        holidays = Holiday.objects.filter(date__gte=timezone.now().date())
        serializer = self.get_serializer(holidays, many=True)
        return Response(serializer.data)