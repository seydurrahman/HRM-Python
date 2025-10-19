from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ProvidentFund
from .serializers import ProvidentFundSerializer

class ProvidentFundViewSet(viewsets.ModelViewSet):
    queryset = ProvidentFund.objects.select_related('employee').all()
    serializer_class = ProvidentFundSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_pf(self, request):
        """Get logged-in employee's provident fund"""
        try:
            employee = request.user.employee_profile
            pf = ProvidentFund.objects.get(employee=employee)
            serializer = self.get_serializer(pf)
            return Response(serializer.data)
        except ProvidentFund.DoesNotExist:
            return Response({'error': 'Provident fund not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)