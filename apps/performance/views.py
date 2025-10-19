from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PerformanceReview
from .serializers import PerformanceReviewSerializer

class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.select_related('employee', 'reviewer').all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'review_type']
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get logged-in employee's performance reviews"""
        try:
            employee = request.user.employee_profile
            reviews = PerformanceReview.objects.filter(employee=employee)
            serializer = self.get_serializer(reviews, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)