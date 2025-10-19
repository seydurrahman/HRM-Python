from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Grievance, DisciplinaryAction
from .serializers import GrievanceSerializer, DisciplinaryActionSerializer

class GrievanceViewSet(viewsets.ModelViewSet):
    queryset = Grievance.objects.select_related('employee', 'assigned_to').all()
    serializer_class = GrievanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'category']
    
    @action(detail=False, methods=['get'])
    def my_grievances(self, request):
        """Get logged-in employee's grievances"""
        try:
            employee = request.user.employee_profile
            grievances = Grievance.objects.filter(employee=employee)
            serializer = self.get_serializer(grievances, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class DisciplinaryActionViewSet(viewsets.ModelViewSet):
    queryset = DisciplinaryAction.objects.select_related('employee', 'issued_by').all()
    serializer_class = DisciplinaryActionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'action_type']