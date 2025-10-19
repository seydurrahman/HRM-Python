from rest_framework import viewsets, filters,status
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, EducationRecord, WorkExperience, Dependent
from .serializers import (
    EmployeeSerializer, EmployeeCreateSerializer,
    EducationRecordSerializer, WorkExperienceSerializer, DependentSerializer
)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department', 'designation').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'designation', 'employment_type', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['date_of_joining', 'employee_id']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get logged-in employee profile"""
        try:
            employee = request.user.employee_profile
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def subordinates(self, request, pk=None):
        """Get employee's subordinates"""
        employee = self.get_object()
        subordinates = Employee.objects.filter(reporting_manager=employee)
        serializer = self.get_serializer(subordinates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get employee statistics"""
        total = Employee.objects.count()
        active = Employee.objects.filter(is_active=True).count()
        by_department = Employee.objects.values('department__name').annotate(
            count=models.Count('id')
        )
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_department': by_department
        })

class EducationRecordViewSet(viewsets.ModelViewSet):
    queryset = EducationRecord.objects.all()
    serializer_class = EducationRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'degree_level']

class WorkExperienceViewSet(viewsets.ModelViewSet):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee']

class DependentViewSet(viewsets.ModelViewSet):
    queryset = Dependent.objects.all()
    serializer_class = DependentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'relationship']