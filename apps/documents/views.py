from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DocumentCategory, Document
from .serializers import DocumentCategorySerializer, DocumentSerializer

class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsAuthenticated]

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('employee', 'category').all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'category']
    
    @action(detail=False, methods=['get'])
    def my_documents(self, request):
        """Get logged-in employee's documents"""
        try:
            employee = request.user.employee_profile
            documents = Document.objects.filter(employee=employee)
            serializer = self.get_serializer(documents, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)