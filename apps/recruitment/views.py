from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import JobPosting, Candidate
from .serializers import JobPostingSerializer, CandidateSerializer

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def active_jobs(self, request):
        """Get active job postings"""
        jobs = JobPosting.objects.filter(status='OPEN')
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.select_related('job_posting').all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['job_posting', 'status']
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update candidate status"""
        candidate = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Candidate.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        candidate.status = new_status
        candidate.save()
        return Response(self.get_serializer(candidate).data)