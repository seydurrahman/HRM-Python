from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import LoanType, Loan
from .serializers import LoanTypeSerializer, LoanSerializer

class LoanTypeViewSet(viewsets.ModelViewSet):
    queryset = LoanType.objects.filter(is_active=True)
    serializer_class = LoanTypeSerializer
    permission_classes = [IsAuthenticated]

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related('employee', 'loan_type').all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'status']
    
    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        """Get logged-in employee's loans"""
        try:
            employee = request.user.employee_profile
            loans = Loan.objects.filter(employee=employee)
            serializer = self.get_serializer(loans, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """Approve or reject loan application"""
        loan = self.get_object()
        action_type = request.data.get('action')
        
        try:
            employee = request.user.employee_profile
            loan.approved_by = employee
            
            if action_type == 'approve':
                loan.status = 'APPROVED'
                loan.approval_date = timezone.now().date()
            elif action_type == 'reject':
                loan.status = 'REJECTED'
            else:
                return Response({'error': 'Invalid action'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            loan.save()
            return Response(self.get_serializer(loan).data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)