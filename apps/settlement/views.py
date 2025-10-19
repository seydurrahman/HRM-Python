from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EmployeeSettlement
from .serializers import EmployeeSettlementSerializer

class EmployeeSettlementViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSettlement.objects.select_related('employee').all()
    serializer_class = EmployeeSettlementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate settlement amount"""
        settlement = self.get_object()
        settlement.calculate_net_amount()
        settlement.status = 'CALCULATED'
        settlement.save()
        return Response(self.get_serializer(settlement).data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve settlement"""
        settlement = self.get_object()
        try:
            employee = request.user.employee_profile
            settlement.status = 'APPROVED'
            settlement.approved_by = employee
            settlement.save()
            return Response(self.get_serializer(settlement).data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)