from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TrainingProgram, TrainingParticipant
from .serializers import TrainingProgramSerializer, TrainingParticipantSerializer

class TrainingProgramViewSet(viewsets.ModelViewSet):
    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming training programs"""
        from django.utils import timezone
        programs = TrainingProgram.objects.filter(
            start_date__gte=timezone.now().date(),
            is_active=True
        )
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

class TrainingParticipantViewSet(viewsets.ModelViewSet):
    queryset = TrainingParticipant.objects.select_related('employee', 'training_program').all()
    serializer_class = TrainingParticipantSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'training_program', 'status']
    
    @action(detail=False, methods=['get'])
    def my_trainings(self, request):
        """Get logged-in employee's trainings"""
        try:
            employee = request.user.employee_profile
            trainings = TrainingParticipant.objects.filter(employee=employee)
            serializer = self.get_serializer(trainings, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)